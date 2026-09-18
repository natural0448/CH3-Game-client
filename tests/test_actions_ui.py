"""Main-thread action panel labels, layout and input behavior."""
import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame

from client.application.queries import QueryStore
from client.application.state import ApplicationState
from client.contracts.queries import read_actions, read_ingest
from client.ui.input import InputRouter
from client.ui.layout import build_layout
from client.ui.panels import draw_actions, draw_ingest
from client.ui.renderer import ScreenRenderer
from client.application.controller import Controller
from client.configuration import load_config
from tests.support import action_snapshot, ingest_summary


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


class ActionUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.display.init()
        pygame.font.init()
        pygame.display.set_mode((1, 1))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_available_and_unavailable_copy(self):
        queries = QueryStore()
        slot = queries.slots["actions"]
        slot.opened = True
        slot.response = {"json": read_actions(action_snapshot()), "message": "done"}
        painter = Recorder()
        draw_actions(painter, slot)
        for expected in ("고정 snapshot · 마지막 집계 기준", "source_topic: game.actions.v1",
                         "source_kind: bounded-kafka-snapshot", "고유 행동 수  10건",
                         "원본 전달 행 수  12행", "이동", "개인 채집", "개인 수련",
                         "방별 행동 수"):
            self.assertIn(expected, painter.labels)
        slot.response = {"json": {"available": False, "summary": None}, "message": "missing"}
        painter = Recorder()
        draw_actions(painter, slot)
        self.assertIn("행동 집계가 아직 없습니다", painter.labels)
        self.assertFalse(any("고유 행동 수" in label for label in painter.labels))

    def test_same_layout_drives_resized_hit_and_login_focus_blocks_direction(self):
        for size in ((1100, 880), (800, 640), (550, 440)):
            layout = build_layout(size)
            viewport, offset = layout.viewport()
            x, y = layout.controls["actions_refresh"].center
            point = (offset[0] + x * viewport[0] / 1100,
                     offset[1] + y * viewport[1] / 880)
            self.assertEqual(layout.hit_test(point, {"actions"}), "actions_refresh")
        router = InputRouter()
        app = ApplicationState()
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)
        self.assertIsNone(router.route(event, build_layout((1100, 880)), app, QueryStore()))
        app.login.focus = None
        self.assertEqual(router.route(event, build_layout((1100, 880)), app, QueryStore()),
                         {"kind": "command", "action": "right"})

    def test_ingest_card_and_unavailable_copy(self):
        queries = QueryStore()
        slot = queries.slots["ingest"]
        slot.opened = True
        slot.response = {"json": read_ingest(ingest_summary()), "message": "done"}
        painter = Recorder()
        draw_ingest(painter, slot)
        for expected in (
            "Kafka 수집 통계", "통계 다시 읽기",
            "이미 게시된 결과만 읽습니다 · Spark 실행 안 함",
            "source: kafka-parquet", "수집 레코드", "고유 사건",
            "재전달 레코드", "player.moved", "player.gathered", "player.trained",
        ):
            self.assertIn(expected, painter.labels)

        slot.response = {"json": {
            "available": False, "reason": "ingest_summary_not_created",
        }, "message": "missing"}
        painter = Recorder()
        draw_ingest(painter, slot)
        self.assertTrue(any("준비되지" in label for label in painter.labels))
        self.assertFalse(any(label == "수집 레코드" for label in painter.labels))

        for size in ((1100, 880), (800, 640), (550, 440)):
            layout = build_layout(size)
            viewport, offset = layout.viewport()
            x, y = layout.controls["ingest_refresh"].center
            point = (offset[0] + x * viewport[0] / 1100,
                     offset[1] + y * viewport[1] / 880)
            self.assertEqual(layout.hit_test(point, {"ingest"}), "ingest_refresh")

    def test_complete_screen_renders_from_read_only_model(self):
        class Port:
            def submit(self, request):
                return True

            def stop(self, timeout=None):
                return None

        screen = pygame.display.set_mode((800, 640))
        controller = Controller(Port())
        layout = build_layout(screen.get_size())
        ScreenRenderer(screen, load_config()).render(controller.screen_model(), layout, 60)
        self.assertEqual(screen.get_size(), (800, 640))


if __name__ == "__main__":
    unittest.main()
