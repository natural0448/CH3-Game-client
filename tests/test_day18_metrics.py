"""Day 18 load and delivery-metric GET contracts and cards."""
import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame

from client.application.queries import QueryStore
from client.application.state import ApplicationState
from client.contracts.auth import Identity
from client.contracts.queries import read_load, read_metrics
from client.network.http import JsonHttpClient
from client.network.queries import QueryGateway
from client.ui.input import InputRouter
from client.ui.layout import build_layout
from client.ui.panels import draw_load, draw_metrics
from tests.support import Response, Session, player


def load_response():
    return {
        "available": True,
        "load": {
            "generated_at": "2026-09-28T06:32:46+00:00",
            "measurement_started_at": "2026-09-28T06:32:16+00:00",
            "profile": {
                "clients": 50, "seconds": 30, "interval_seconds": 1.0,
                "players_per_room": 20, "asgi_processes": 1,
            },
            "connected_success": 48, "connected_peak": 48,
            "attempt_count": 1484, "success_count": 1484, "error_count": 2,
            "elapsed_seconds": 30.464, "success_per_second": 48.713,
            "rtt_sample_count": 1484, "rtt_mean_ms": 90.0, "rtt_p95_ms": 500.036,
            "by_room": [
                {"room_id": "load18-01", "connected": 20, "success_count": 600},
                {"room_id": "load18-02", "connected": 20, "success_count": 600},
                {"room_id": "load18-03", "connected": 8, "success_count": 284},
            ],
        },
    }


def metrics_response():
    return {
        "available": True,
        "metrics": {
            "schema_version": 1,
            "generated_at": "2026-09-28T07:30:00+00:00",
            "window_start": "2026-09-28T07:28:00+00:00",
            "window_end": "2026-09-28T07:30:00+00:00",
            "window_seconds": 120,
            "confirmed_count": 12,
            "confirmed_per_second": 0.1,
            "published_recent": 10,
            "pending_mark_count": 2,
            "oldest_pending_age_seconds": 3.5,
            "by_action": [{"event_type": "player.moved", "count": 12}],
            "by_room": [{"room_id": "load18-01", "count": 12}],
            "kafka": {
                "topic": "game.events.v1",
                "group_id": "village-actions-v1",
                "partitions": [{
                    "topic": "game.events.v1", "partition": 0,
                    "beginning_offset": 0, "end_offset": 12,
                    "committed_offset": 10, "within_retention": True, "lag": 2,
                }],
                "known_lag_sum": 2,
                "lag_complete": False,
            },
            "spark_progress": {
                "id": "query-id", "runId": "run-id", "name": "game-actions-delta-v1",
                "timestamp": "2026-09-28T07:29:00+00:00", "batchId": 10,
                "numInputRows": 25, "inputRowsPerSecond": 5.0,
                "processedRowsPerSecond": 4.0,
            },
        },
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


class Day18GatewayTests(unittest.IsolatedAsyncioTestCase):
    async def test_gets_use_the_authenticated_session_and_allowlisted_json(self):
        for kind, response, path in (
            ("load", load_response(), "/api/analytics/load/"),
            ("metrics", metrics_response(), "/api/analytics/metrics/"),
        ):
            auth = FakeAuth(Response(data=response))
            events = []
            gateway = QueryGateway(
                auth, lambda event_kind, **data: events.append({"kind": event_kind, **data})
            )
            gateway.set_identity(Identity(1, "room-01", 0, player()))
            await gateway.fetch({
                "kind": kind, "request_id": kind + "-id", "player_id": 1,
            })
            args, kwargs = auth.session.calls[0]
            self.assertEqual(args, ("GET", "http://127.0.0.1:8000" + path))
            self.assertFalse(kwargs["allow_redirects"])
            self.assertEqual(kwargs["timeout"].total, 8)
            self.assertNotIn("cookie", str(events[0]).lower())

    async def test_unavailable_and_login_response_are_not_numbers(self):
        for kind, payload in (
            ("load", {"available": False, "load": None}),
            ("metrics", {"available": False, "metrics": None}),
        ):
            events = []
            gateway = QueryGateway(
                FakeAuth(Response(data=payload)),
                lambda event_kind, **data: events.append({"kind": event_kind, **data}),
            )
            gateway.set_identity(Identity(1, "room-01", 0, player()))
            await gateway.fetch({"kind": kind, "request_id": kind, "player_id": 1})
            self.assertEqual(events[0]["message"], "아직 측정 전")

            events.clear()
            gateway = QueryGateway(
                FakeAuth(Response(status=401, content_type="text/html", raw=b"private")),
                lambda event_kind, **data: events.append({"kind": event_kind, **data}),
            )
            gateway.set_identity(Identity(1, "room-01", 0, player()))
            await gateway.fetch({"kind": kind, "request_id": kind, "player_id": 1})
            self.assertIn("로그인", events[0]["message"])
            self.assertNotIn("private", str(events[0]))


class Day18UiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.display.init()
        pygame.font.init()
        pygame.display.set_mode((1, 1))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_load_card_keeps_units_and_room_scope(self):
        slot = QueryStore().slots["load"]
        slot.opened = True
        slot.response = {"json": read_load(load_response())}
        painter = Recorder()
        draw_load(painter, slot)
        for expected in (
            "최근 수업 측정", "연결 성공 48개", "RTT p95 500.036ms",
            "이번 실행의 최다 응답 방: load18-01 · 600건",
            "방별 이번 부하 실행 결과",
            "이 표는 이번 부하 실행의 결과입니다. 현재 온라인 인원이 아닙니다.",
        ):
            self.assertTrue(any(expected in label for label in painter.labels))

        missing = QueryStore().slots["load"]
        missing.opened = True
        missing.response = {"json": {"available": False, "load": None}}
        painter = Recorder()
        draw_load(painter, missing)
        self.assertIn("아직 측정 전", painter.labels)
        self.assertFalse(any("0ms" in label for label in painter.labels))

    def test_metrics_card_keeps_generated_and_spark_times_separate(self):
        slot = QueryStore().slots["metrics"]
        slot.opened = True
        slot.response = {"json": read_metrics(metrics_response())}
        painter = Recorder()
        draw_metrics(painter, slot)
        self.assertTrue(any(label.startswith("지표 생성 시각:") for label in painter.labels))
        self.assertTrue(any(label.startswith("Spark 기록 시각:") for label in painter.labels))
        self.assertTrue(any("일부 위치 미확인" in label for label in painter.labels))

    def test_refresh_controls_route_without_touching_game_state(self):
        router = InputRouter()
        for kind in ("load", "metrics"):
            layout = build_layout((800, 640))
            viewport, offset = layout.viewport()
            x, y = layout.controls[kind + "_refresh"].center
            point = (
                offset[0] + x * viewport[0] / 1100,
                offset[1] + y * viewport[1] / 880,
            )
            event = pygame.event.Event(
                pygame.MOUSEBUTTONDOWN, button=1, pos=point
            )
            queries = QueryStore()
            queries.slots[kind].opened = True
            self.assertEqual(
                router.route(event, layout, ApplicationState(), queries),
                {"kind": "query", "query": kind},
            )


if __name__ == "__main__":
    unittest.main()
