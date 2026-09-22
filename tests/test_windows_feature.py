"""Time-window response, worker request and main-thread panel behavior."""
import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame

from client.application.queries import QueryStore
from client.application.state import ApplicationState
from client.contracts.auth import Identity
from client.contracts.queries import read_windows
from client.network.http import JsonHttpClient
from client.network.queries import QueryGateway
from client.ui.input import InputRouter
from client.ui.layout import build_layout
from client.ui.panels import draw_windows
from tests.support import Response, Session, player


def window_summary():
    return {
        "available": True,
        "generated_at": "2026-09-22T13:00:00+09:00",
        "windows": [
            {
                "kind": kind,
                "window_start": f"2026-09-22T12:59:{second:02d}+09:00",
                "window_end": f"2026-09-22T13:00:{second - 50:02d}+09:00",
                "event_type": "player.moved",
                "count": index + 1,
                "ignored": "not exposed",
            }
            for index, (kind, second) in enumerate((
                ("tumbling", 50), ("sliding", 51), ("tumbling", 52),
                ("sliding", 53), ("tumbling", 54), ("sliding", 55),
            ))
        ],
        "session": "must not be exposed",
    }


class FakeAuth:
    def __init__(self, response):
        self.session = Session(response)
        self.http = JsonHttpClient(
            self.session, "http://127.0.0.1:8000", 8, "http://127.0.0.1:8000"
        )

    async def request_json(self, method, path, *, payload=None, csrf=False):
        return await self.http.request_json(method, path, payload=payload)


class Recorder:
    def __init__(self):
        self.canvas = pygame.Surface((1100, 880))
        self.fonts = {size: pygame.font.Font(None, size) for size in (13, 15, 17, 20, 26, 32)}
        self.layout = build_layout((1100, 880))
        self.labels = []

    def text(self, value, *args, **kwargs):
        self.labels.append(str(value))

    def wrapped(self, value, *args, **kwargs):
        self.labels.append(str(value))

    def card(self, *args, **kwargs):
        return None

    def button(self, name, label, enabled=True):
        self.labels.append(str(label))


class WindowsGatewayTests(unittest.IsolatedAsyncioTestCase):
    async def test_get_uses_existing_session_and_safe_allowlist(self):
        auth = FakeAuth(Response(data=window_summary()))
        events = []
        gateway = QueryGateway(auth, lambda kind, **data: events.append({"kind": kind, **data}))
        gateway.set_identity(Identity(1, "room-01", 0, player()))

        await gateway.fetch({"kind": "windows", "request_id": "window-id", "player_id": 1})

        args, kwargs = auth.session.calls[0]
        self.assertEqual(args, ("GET", "http://127.0.0.1:8000/api/analytics/windows/"))
        self.assertFalse(kwargs["allow_redirects"])
        self.assertEqual(kwargs["timeout"].total, 8)
        self.assertNotIn("session", events[0]["json"])
        self.assertNotIn("ignored", events[0]["json"]["windows"][0])

    async def test_unavailable_is_not_presented_as_zero(self):
        auth = FakeAuth(Response(data={"available": False, "windows": []}))
        events = []
        gateway = QueryGateway(auth, lambda kind, **data: events.append({"kind": kind, **data}))
        gateway.set_identity(Identity(1, "room-01", 0, player()))
        await gateway.fetch({"kind": "windows", "request_id": "missing", "player_id": 1})
        self.assertEqual(events[0]["message"], "아직 창 요약이 없습니다")
        self.assertEqual(events[0]["json"], {"available": False, "windows": []})


class WindowsUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.display.init()
        pygame.font.init()
        pygame.display.set_mode((1, 1))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_panel_shows_five_recent_rows_and_filters_without_request(self):
        queries = QueryStore()
        slot = queries.slots["windows"]
        slot.opened = True
        slot.response = {"json": read_windows(window_summary()), "message": "done"}
        painter = Recorder()
        draw_windows(painter, slot)
        self.assertIn("확정 시간 창의 전달 레코드 수(중복 전달 포함 가능)", painter.labels)
        self.assertIn("시작 시각 포함 · 끝 시각 미포함", painter.labels)
        self.assertIn("tumbling", painter.labels)
        self.assertIn("sliding", painter.labels)
        self.assertTrue(any(label.startswith("tumbling ·") for label in painter.labels))
        self.assertTrue(any(label.startswith("sliding ·") for label in painter.labels))
        self.assertIn("최근 5행 · 필터는 받은 결과에만 적용 · 합계는 고유 사건 수가 아닙니다.", painter.labels)
        self.assertEqual(sum("player.moved" in label for label in painter.labels), 5)

        self.assertTrue(queries.set_filter("windows", "tumbling"))
        painter = Recorder()
        draw_windows(painter, slot)
        self.assertEqual(sum("player.moved" in label for label in painter.labels), 3)
        self.assertFalse(slot.busy)
        self.assertIsNone(slot.request_id)

    def test_empty_states_and_filter_hit_are_distinct(self):
        queries = QueryStore()
        slot = queries.slots["windows"]
        slot.opened = True
        slot.response = {"json": {"available": False, "windows": []}}
        painter = Recorder()
        draw_windows(painter, slot)
        self.assertIn("아직 창 요약이 없습니다", painter.labels)
        self.assertFalse(any("0건" in label for label in painter.labels))

        slot.response = {"json": {
            "available": True,
            "generated_at": "2026-09-22T13:00:00+09:00",
            "windows": [],
        }}
        painter = Recorder()
        draw_windows(painter, slot)
        self.assertIn("확정된 게시 대상 창이 없습니다", painter.labels)

        layout = build_layout((800, 640))
        viewport, offset = layout.viewport()
        x, y = layout.controls["windows_filter_sliding"].center
        point = (offset[0] + x * viewport[0] / 1100, offset[1] + y * viewport[1] / 880)
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=point)
        intent = InputRouter().route(event, layout, ApplicationState(), queries)
        self.assertEqual(intent, {
            "kind": "panel_filter", "query": "windows", "value": "sliding",
        })


if __name__ == "__main__":
    unittest.main()
