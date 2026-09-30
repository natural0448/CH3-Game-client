"""Lake snapshot contract, same-session GET and main-thread panel regressions."""
import asyncio
import copy
import os
import unittest
from unittest.mock import AsyncMock, Mock

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame
from yarl import URL

from client.application.controller import Controller
from client.application.queries import QueryStore
from client.application.state import ApplicationState
from client.contracts.auth import Identity
from client.contracts.queries import read_lake
from client.network.queries import QueryGateway
from client.network.session import AuthSession
from client.network.worker import NetworkWorker
from client.ui.input import InputRouter
from client.ui.layout import build_layout
from client.ui.panels import draw_api, draw_lake, draw_query_panels
from client.ui.sections.activity import draw_activity
from tests.support import Response, player
from tests.test_day18_metrics import Recorder
from tests.test_network_queries import FakeAuth


def lake_response(**changes):
    return {
        "schema_version": 1, "status": "ready", "dataset_version": "capture-002",
        "rows": 5766, "bytes": 4590247,
        "captured_at": "2026-09-30T00:00:00+00:00",
        "generated_at": "2026-09-30T00:02:00+00:00",
        "matched": True, "verification_scope": "local-and-copied-bytes",
        **changes,
    }


class LakeContractTests(unittest.TestCase):
    def test_ready_copies_only_small_public_fields(self):
        payload = lake_response(events=[{"player_id": 99}], player_ids=[99],
                                cookie="private", csrfToken="private", password="private")
        parsed = read_lake(payload)
        self.assertEqual(parsed["rows"], 5766)
        for field in ("events", "player_ids", "cookie", "csrfToken", "password"):
            self.assertNotIn(field, parsed)

    def test_pending_and_unavailable_do_not_invent_measurements(self):
        for status in ("pending", "unavailable"):
            self.assertEqual(read_lake(lake_response(status=status)),
                             {"schema_version": 1, "status": status, "available": False})

    def test_invalid_verification_types_and_times_are_rejected(self):
        for change in ({"matched": "true"}, {"rows": -1}, {"bytes": True},
                       {"schema_version": True}, {"status": "unknown"},
                       {"verification_scope": "all-remote-copies"},
                       {"generated_at": "2026-09-30T00:00:00"}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                read_lake(lake_response(**change))


class LakeGatewayTests(unittest.IsolatedAsyncioTestCase):
    async def fetch(self, response):
        auth = FakeAuth(response)
        events = []
        gateway = QueryGateway(auth, lambda kind, **data: events.append({"kind": kind, **data}))
        gateway.set_identity(Identity(1, "room-01", 0, player()))
        await gateway.fetch({"kind": "lake", "request_id": "lake-id", "player_id": 1})
        return auth, events[0]

    async def test_get_uses_existing_session_policy_and_worker_registration(self):
        auth, event = await self.fetch(Response(data=lake_response()))
        args, kwargs = auth.session.calls[0]
        self.assertEqual(args, ("GET", "http://127.0.0.1:8000/api/analytics/lake/"))
        self.assertFalse(kwargs["allow_redirects"])
        self.assertEqual(kwargs["timeout"].total, 8)
        self.assertEqual(event["json"]["dataset_version"], "capture-002")
        self.assertIn("lake", NetworkWorker.QUERY_KINDS)

    async def test_redirect_unauthorized_and_html_are_login_guidance_without_body(self):
        for status in (302, 401, 200):
            response = Response(status=status, content_type="text/html", raw=b"private body")
            _, event = await self.fetch(response)
            self.assertFalse(response.body_read)
            self.assertIsNone(event["json"])
            self.assertIn("로그인", event["message"])
            self.assertNotIn("private", str(event))

    async def test_pending_unavailable_and_503_keep_distinct_messages(self):
        _, pending = await self.fetch(Response(data=lake_response(status="pending")))
        _, unavailable = await self.fetch(Response(data=lake_response(status="unavailable")))
        _, failed = await self.fetch(Response(status=503, raw=b"private"))
        self.assertIn("준비 중", pending["message"])
        self.assertIn("조회 불가", unavailable["message"])
        self.assertIn("조회 불가", failed["message"])
        self.assertIsNone(failed["json"])

    async def test_network_timeout_and_missing_login_do_not_emit_counts(self):
        auth = Mock()
        auth.request_json = AsyncMock(side_effect=asyncio.TimeoutError)
        events = []
        gateway = QueryGateway(auth, lambda kind, **data: events.append({"kind": kind, **data}))
        request = {"kind": "lake", "request_id": "lake-id", "player_id": 1}
        await gateway.fetch(request)
        auth.request_json.assert_not_called()
        self.assertIn("로그인", events[-1]["message"])
        gateway.set_identity(Identity(1, "room-01", 0, player()))
        await gateway.fetch(request)
        self.assertIsNone(events[-1]["json"])
        self.assertIn("조회 불가", events[-1]["message"])

    async def test_ip_cookies_are_allowed_only_on_loopback_and_sessions_are_independent(self):
        for base, accepts_cookie in (("http://127.0.0.1:8000", True),
                                     ("http://[::1]:8000", True),
                                     ("http://localhost:8000", True),
                                     ("http://192.0.2.1:8000", False)):
            auth = AuthSession({"server_base_url": base})
            await auth.open()
            session = auth.session
            session.cookie_jar.update_cookies({"sessionid": "test-only"}, response_url=URL(base))
            self.assertEqual("sessionid" in session.cookie_jar.filter_cookies(URL(base)), accepts_cookie)
            other = AuthSession({"server_base_url": base})
            try:
                await other.open()
                self.assertFalse(other.session.cookie_jar.filter_cookies(URL(base)))
            finally:
                await auth.close()
                await other.close()
            self.assertTrue(session.closed)


class LakeUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.display.init()
        pygame.font.init()
        pygame.display.set_mode((1, 1))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_ready_panel_displays_scope_times_and_match_both_ways(self):
        for matched, label in ((True, "마지막 로컬 사본과 일치"),
                               (False, "원본 비교 확인 필요")):
            slot = QueryStore().slots["lake"]
            slot.opened = True
            slot.response = {"json": read_lake(lake_response(matched=matched))}
            painter = Recorder()
            draw_lake(painter, slot)
            for expected in ("원본 보존", "capture-002", "5,766행", "4,590,247 bytes",
                             "captured_at", "generated_at", label, "local-and-copied-bytes",
                             "선택한 원본과 로컬 사본을 마지막으로 검사한 결과"):
                self.assertTrue(any(expected in value for value in painter.labels), expected)

    def test_pending_and_unavailable_panels_have_no_fake_zero(self):
        for status, message in (("pending", "준비 중"), ("unavailable", "조회 불가")):
            store = QueryStore()
            slot = store.slots["lake"]
            slot.opened = True
            slot.response = {"json": read_lake(lake_response(status=status))}
            painter = Recorder()
            draw_query_panels(painter, store.slots)
            self.assertTrue(any(message in value for value in painter.labels))
            self.assertFalse(any("0행" in value or "0 bytes" in value for value in painter.labels))

    def test_refresh_and_entry_hit_testing_survive_resize_with_ad_slots_preserved(self):
        queries = QueryStore()
        app = ApplicationState()
        for size in ((1100, 880), (800, 640), (320, 240)):
            layout = build_layout(size)
            for control in ("lake", "lake_refresh"):
                queries.slots["lake"].opened = control.endswith("refresh")
                viewport, offset = layout.viewport()
                x, y = layout.controls[control].center
                point = (offset[0] + x * viewport[0] / 1100,
                         offset[1] + y * viewport[1] / 880)
                event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=point)
                self.assertEqual(InputRouter().route(event, layout, app, queries),
                                 {"kind": "query", "query": "lake"})
            self.assertEqual(set(layout.slots), {"village-board", "lobby-banner"})
            self.assertEqual(layout.ad_slots["village-ad-slot"], pygame.Rect(40, 740, 278, 58))
            self.assertEqual(layout.ad_slots["lobby-ad-slot"], pygame.Rect(710, 788, 342, 24))

    def test_single_queue_request_and_response_do_not_change_game_state(self):
        network = Mock()
        network.submit.return_value = True
        controller = Controller(network)
        controller.game.apply_identity(player(x=2, y=2, coins=10, version=4))
        controller.app.phase = "connected"
        before = copy.deepcopy(controller.game)
        controller.handle_intent({"kind": "query", "query": "lake"})
        controller.handle_intent({"kind": "query", "query": "lake"})
        network.submit.assert_called_once()
        request = network.submit.call_args.args[0]
        self.assertEqual(request["kind"], "lake")
        controller.handle_network_event({**request, "path": "GET /api/analytics/lake/",
                                         "status": 200, "json": read_lake(lake_response())})
        self.assertEqual(controller.game, before)
        painter = Recorder()
        draw_api(painter, controller.queries.slots["lake"], "lake", 0)
        self.assertIn("GET /api/analytics/lake/", painter.labels)
        controller.app.show_api = True
        model = controller.screen_model()
        draw_activity(painter, model.app, model.game, model.queries)
        self.assertIn("원본 보존 응답", painter.labels)
        controller.handle_intent({"kind": "query", "query": "lake"})
        self.assertEqual(network.submit.call_count, 2)


if __name__ == "__main__":
    unittest.main()
