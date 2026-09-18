"""Offline checks: train acknowledgements, private history and async HTTP."""
import asyncio
import copy
import unittest
from uuid import uuid4

from history_data import read_history
from network import NetworkWorker
from panels import HistoryPanel
from state import VillageState
from test_delivery_client import Response, Session
from test_multiplayer import player


def history_data():
    return {"scope": "current-player", "limit": 20, "events": [{
        "schema_version": 1, "event_id": str(uuid4()), "event_type": "player.trained",
        "player_id": 1, "room_id": "room-01", "event_time": "2026-09-16T07:00:00+00:00",
        "payload": {"x": 3, "y": 2, "coins": 1, "version": 6, "transition": {
            "episode_id": str(uuid4()), "step": 1, "reward": 1,
            "observation": {"x": 3, "y": 2, "coins": 0},
            "next_observation": {"x": 3, "y": 2, "coins": 1},
            "action": {"type": "train"}, "done": False, "terminated": False,
            "truncated": False, "policy_version": "manual-v1",
        }},
    }]}


class TrainStateTests(unittest.TestCase):
    def setUp(self):
        self.state = VillageState()
        self.state.accept({"kind": "identity", "data": player(x=3, y=2)})
        self.state.accept({"kind": "status", "phase": "connecting", "epoch": 1, "message": "wait"})
        self.state.accept({"kind": "state", "data": player(x=3, y=2), "epoch": 1, "first": True})

    def test_train_payload_and_matching_ack_keeps_history_closed(self):
        state = self.state
        panel = HistoryPanel()
        request = state.command("train", now=1)
        command_id = request["command"]["command_id"]
        self.assertEqual(set(request["command"]), {"type", "command_id"})
        self.assertEqual(request["command"]["type"], "train")
        self.assertIsNone(state.command("train", now=2))
        self.assertEqual(state.own["coins"], 0)
        state.accept({"kind": "state", "epoch": 1, "data": player(2, command_id=command_id, coins=1, version=1)})
        self.assertEqual(state.pending, command_id)
        self.assertFalse(panel.opened)
        state.accept({"kind": "state", "epoch": 1, "data": player(x=3, y=2, command_id="unrelated", coins=1, version=1)})
        self.assertEqual(state.own["coins"], 0)
        self.assertEqual(state.pending, command_id)
        state.accept({"kind": "state", "epoch": 1, "data": player(x=3, y=2, command_id=command_id, coins=1, version=1)})
        self.assertIsNone(state.pending)
        self.assertEqual(state.own["coins"], 1)
        panel.accept({"kind": "state", "epoch": 1, "data": state.own}, state)
        self.assertFalse(panel.opened)
        self.assertFalse(panel.busy)
        self.assertIn("수련 완료", state.message)
        self.assertIsNone(state.command("train", now=1.1))
        state.clear_account()
        self.assertIsNone(state.pending_action)

    def test_tile_first_state_disconnect_and_error_gates(self):
        state = self.state
        state.has_ws_state = False
        self.assertIsNone(state.command("train", now=1))
        state.has_ws_state = True
        state.own["x"] = 2
        self.assertIsNone(state.command("train", now=1))
        state.own["x"] = 3
        request = state.command("train", now=1)
        state.accept({"kind": "error", "epoch": 1, "command_id": request["command"]["command_id"], "code": "not_at_train_tile"})
        self.assertIsNone(state.pending_action)
        self.assertEqual(state.own["coins"], 0)
        state.accept({"kind": "status", "phase": "disconnected", "epoch": 1, "message": "lost"})
        self.assertIsNone(state.command("train", now=2))

    def test_history_panel_ignores_other_or_stale_requests_and_clears_on_logout(self):
        panel = HistoryPanel()
        request = panel.request(self.state)
        self.assertEqual(request["kind"], "history")
        event = dict(kind="history", request_id=request["request_id"], player_id=2)
        panel.accept(event, self.state)
        self.assertTrue(panel.busy)
        event.update(player_id=1, path="GET /api/history/", status=200, json=history_data(), message="done")
        original = copy.deepcopy(self.state.own)
        panel.accept(event, self.state)
        self.assertFalse(panel.busy)
        self.assertEqual(self.state.own, original)
        panel.accept({"kind": "logged_out"}, self.state)
        self.assertIsNone(panel.response)


class HistoryNetworkTests(unittest.IsolatedAsyncioTestCase):
    def worker(self, response):
        worker = NetworkWorker({"server_base_url": "http://127.0.0.1:8000"})
        worker.identity = 1
        worker.session = Session(response)
        return worker

    async def test_same_session_sanitized_queue_and_missing_transition(self):
        data = history_data()
        data["password"] = "exclude-me"
        data["events"][0]["payload"]["transition"]["action"]["token"] = "exclude-me"
        worker = self.worker(Response(data=data))
        worker.pending = "game-command"
        await worker._history({"player_id": 1, "request_id": "read-1"})
        event = worker.events.get_nowait()
        self.assertEqual(event["status"], 200)
        self.assertEqual(event["request_id"], "read-1")
        self.assertNotIn("exclude-me", str(event))
        args, kwargs = worker.session.calls[0]
        self.assertEqual(args, ("GET", "http://127.0.0.1:8000/api/history/"))
        self.assertFalse(kwargs["allow_redirects"])
        self.assertEqual(kwargs["timeout"].total, 8)
        self.assertEqual(worker.pending, "game-command")
        del data["events"][0]["payload"]["transition"]
        self.assertNotIn("transition", read_history(data, 1)["events"][0]["payload"])
        with self.assertRaises(ValueError):
            read_history(data, 2)

    async def test_html_and_login_responses_are_not_parsed(self):
        for status in (200, 302, 401):
            response = Response(status=status, content_type="text/html", raw=b"private")
            worker = self.worker(response)
            await worker._history({"player_id": 1})
            event = worker.events.get_nowait()
            self.assertIsNone(event["json"])
            self.assertFalse(response.body_read)
            if status != 200:
                self.assertIn("로그인", event["message"])

    async def test_slow_history_does_not_block_commands_and_cleanup_cancels_it(self):
        worker = self.worker(Response(data={}))
        started, moved, cancelled = asyncio.Event(), asyncio.Event(), asyncio.Event()
        async def slow_history(request):
            started.set()
            try:
                await asyncio.Event().wait()
            finally:
                cancelled.set()
        async def command(request):
            moved.set()
        async def close():
            pass
        worker._history, worker._command = slow_history, command
        worker.session.close = close
        worker.session.cookie_jar = type("Jar", (), {"clear": lambda self: None})()
        task = asyncio.create_task(worker._run())
        try:
            worker.submit({"kind": "history"})
            await asyncio.wait_for(started.wait(), 1)
            worker.submit({"kind": "command"})
            await asyncio.wait_for(moved.wait(), 1)
        finally:
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)
        self.assertTrue(cancelled.is_set())


if __name__ == "__main__":
    unittest.main()
