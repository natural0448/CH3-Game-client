"""Offline action snapshot contract, queue lifecycle and presentation checks."""
import asyncio
import copy
import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

from actions_panel import ActionsPanel
from analytics_data import read_actions
from network import NetworkWorker
from state import VillageState
from test_delivery_client import Response, Session
from test_multiplayer import player


def snapshot():
    return {
        "available": True, "source_topic": "game.actions.v1",
        "source_kind": "bounded-kafka-snapshot", "raw_record_count": 12,
        "label_source": "current-display-map",
        "bounds": [{"partition": 0, "start_inclusive": 0, "end_exclusive": 12}],
        "summary": {
            "generated_at": "2026-09-17T07:24:52+00:00", "event_count": 10,
            "by_action": [
                {"event_type": "player.moved", "action_label": "이동", "count": 7},
                {"event_type": "player.gathered", "action_label": "개인 채집", "count": 2},
                {"event_type": "player.trained", "action_label": "개인 수련", "count": 1},
            ],
            "by_room": [{"room_id": "room-01", "count": 10}],
        },
    }


class ActionContractTests(unittest.TestCase):
    def test_allowlist_and_original_data_unchanged(self):
        data = snapshot()
        data["csrfToken"] = "private"
        data["summary"]["cookie"] = "private"
        data["summary"]["by_action"][0]["password"] = "private"
        data["bounds"][0]["session"] = "private"
        before = copy.deepcopy(data)
        clean = read_actions(data)
        self.assertNotIn("private", str(clean))
        self.assertEqual(data, before)
        self.assertEqual(clean["summary"]["event_count"], 10)
        self.assertEqual(clean["raw_record_count"], 12)

    def test_unavailable_is_not_zero_and_zero_is_a_real_result(self):
        self.assertEqual(read_actions({"available": False, "event_count": 0}),
                         {"available": False, "summary": None})
        data = snapshot()
        data["raw_record_count"] = data["summary"]["event_count"] = 0
        data["summary"]["by_action"] = []
        data["summary"]["by_room"] = []
        self.assertEqual(read_actions(data)["summary"]["event_count"], 0)

    def test_malformed_metrics_are_rejected(self):
        bad = []
        for key, value in (("raw_record_count", True), ("source_kind", "live"), ("available", 1)):
            data = snapshot()
            data[key] = value
            bad.append(data)
        for key, value in (("generated_at", "2026-09-17"), ("event_count", -1), ("by_room", None)):
            data = snapshot()
            data["summary"][key] = value
            bad.append(data)
        data = snapshot()
        data["summary"]["by_action"][1] = data["summary"]["by_action"][0]
        bad.append(data)
        for data in bad:
            with self.subTest(data=data), self.assertRaises(ValueError):
                read_actions(data)

    def test_panel_correlates_requests_and_never_mutates_game_state(self):
        state = VillageState(phase="connected", own=player(), pending="move-id")
        before = copy.deepcopy(state)
        panel = ActionsPanel()
        request = panel.request(state)
        self.assertIsNone(panel.request(state))
        event = dict(kind="actions", request_id="old", player_id=1,
                     path="GET /api/analytics/actions/", status=200, json=read_actions(snapshot()), message="done")
        panel.accept(event, state)
        self.assertTrue(panel.busy)
        event["request_id"] = request["request_id"]
        event["player_id"] = 2
        panel.accept(event, state)
        self.assertTrue(panel.busy)
        event["player_id"] = 1
        state.accept(event)
        panel.accept(event, state)
        self.assertFalse(panel.busy)
        self.assertEqual(state, before)
        panel.accept({"kind": "logged_out"}, state)
        panel.accept(event, state)
        self.assertIsNone(panel.response)


class ActionNetworkTests(unittest.IsolatedAsyncioTestCase):
    def worker(self, response):
        worker = NetworkWorker({"server_base_url": "http://127.0.0.1:8000"})
        worker.session = Session(response)
        worker.identity = 1
        worker.pending = "move-id"
        return worker

    async def test_get_same_session_and_safe_queue(self):
        worker = self.worker(Response(data=snapshot()))
        session = worker.session
        await worker._actions({"request_id": "query-id", "player_id": 1})
        result = worker.events.get_nowait()
        self.assertEqual(result["kind"], "actions")
        self.assertEqual(result["request_id"], "query-id")
        self.assertEqual(result["json"]["summary"]["event_count"], 10)
        self.assertEqual(worker.pending, "move-id")
        self.assertIs(worker.session, session)
        args, kwargs = session.calls[0]
        self.assertEqual(args, ("GET", "http://127.0.0.1:8000/api/analytics/actions/"))
        self.assertFalse(kwargs["allow_redirects"])
        self.assertEqual(kwargs["timeout"].total, 8)

    async def test_redirect_html_timeout_and_missing_are_not_zero(self):
        for status in (302, 401, 404, 500, 200):
            response = Response(status=status, content_type="text/html", raw=b"private cookie")
            worker = self.worker(response)
            await worker._actions({"player_id": 1})
            result = worker.events.get_nowait()
            self.assertFalse(response.body_read)
            self.assertIsNone(result["json"])
            self.assertNotIn("private", str(result))
            if status in (302, 401):
                self.assertIn("로그인", result["message"])
        worker = self.worker(Response(data={"available": False}))
        await worker._actions({"player_id": 1})
        self.assertEqual(worker.events.get_nowait()["message"], "행동 집계가 아직 없습니다")
        async def timeout(*args):
            raise asyncio.TimeoutError()
        worker._json = timeout
        await worker._actions({"player_id": 1})
        self.assertIsNone(worker.events.get_nowait()["json"])

    async def test_slow_query_keeps_command_queue_live_and_cancels_on_close(self):
        worker = self.worker(Response(data=snapshot()))
        worker.pending = None
        started, moved, cancelled = asyncio.Event(), asyncio.Event(), asyncio.Event()
        async def slow_json(*args):
            started.set()
            try:
                await asyncio.Event().wait()
            finally:
                cancelled.set()
        async def command(request):
            moved.set()
        async def close():
            pass
        worker._json, worker._command = slow_json, command
        worker.session.close = close
        worker.session.cookie_jar = type("Jar", (), {"clear": lambda self: None})()
        task = asyncio.create_task(worker._run())
        try:
            # No unsolicited GET before a button request reaches the queue.
            await asyncio.sleep(.02)
            self.assertFalse(started.is_set())
            worker.submit({"kind": "actions", "request_id": "query-id", "player_id": 1})
            await asyncio.wait_for(started.wait(), 1)
            worker.submit({"kind": "command"})
            await asyncio.wait_for(moved.wait(), 1)
        finally:
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)
        self.assertTrue(cancelled.is_set())
        self.assertIsNone(worker.actions_task)
        self.assertIsNone(worker.session)


class ActionRenderingTests(unittest.TestCase):
    def test_panel_states_and_resized_refresh_hit(self):
        import pygame
        from render import Renderer
        pygame.display.init()
        pygame.font.init()
        try:
            renderer = Renderer(pygame.display.set_mode((1100, 880)))
            state = VillageState(phase="connected", own=player())
            panel = renderer.actions
            panel.opened = True
            for data, message, expected in (
                (read_actions(snapshot()), "done", "고유 행동 수  10건"),
                ({"available": False, "summary": None}, "missing", "행동 집계가 아직 없습니다"),
                (None, "다시 로그인해 주세요.", "다시 로그인해 주세요."),
            ):
                labels = []
                original = renderer.text
                def record(text, *args, **kwargs):
                    labels.append(str(text))
                    return original(text, *args, **kwargs)
                renderer.text = record
                panel.response = {"json": data, "message": message}
                panel.draw(renderer)
                renderer.text = original
                self.assertIn(expected, labels)
                if data is None or not data["available"]:
                    self.assertFalse(any("고유 행동 수" in line for line in labels))
            for size in ((1100, 880), (800, 640), (550, 440)):
                renderer.screen = pygame.display.set_mode(size)
                renderer.draw(state, "", "", None, 60)
                viewport, offset = renderer.viewport()
                x, y = panel.controls()["actions_refresh"].center
                point = (offset[0] + x * viewport[0] / 1100, offset[1] + y * viewport[1] / 880)
                self.assertEqual(renderer.hit_test(point), "actions_refresh")
        finally:
            pygame.quit()


if __name__ == "__main__":
    unittest.main()
