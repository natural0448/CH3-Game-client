"""Pygame rendering and hit testing. Call only from the main thread."""

import json
import threading
from pathlib import Path

import pygame

from state import GATHER_TILE, TRAIN_TILE, HEIGHT, TILE, WIDTH
from panels import AnalyticsPanel, HistoryPanel, draw_api
from world import draw_world
from actions_panel import ActionsPanel

CANVAS = (1100, 880)
INK = (33, 53, 49)
MUTED = (100, 116, 105)
GREEN = (29, 105, 83)
CREAM = (245, 244, 234)
WHITE = (255, 254, 247)
LINE = (219, 224, 208)
PHASES = {
    "signed_out": "로그인 전", "authenticating": "로그인 확인 중",
    "connecting": "첫 상태 대기", "connected": "마을 연결됨",
    "disconnected": "연결 끊김", "reconnecting": "재연결 중",
    "logging_out": "로그아웃 중", "stopped": "종료됨",
}


class Renderer:
    def __init__(self, screen, config=None):
        assert threading.current_thread() is threading.main_thread()
        self.screen = screen
        self.canvas = pygame.Surface(CANVAS)
        self.analytics = AnalyticsPanel()
        self.history = HistoryPanel()
        self.actions = ActionsPanel()
        self.query_panels = {"analytics": self.analytics, "history": self.history, "actions": self.actions}
        self.api_source = "delivery"
        self.api_scroll = 0
        root = Path(__file__).resolve().parent
        if config is None:
            config = json.loads((root / "config.json").read_text(encoding="utf-8"))
        assets = root / config.get("assets_dir", "assets")
        self.asset_notice = ""
        font_path = assets / config.get("font_path", "fonts/NotoSansCJKkr-Regular.otf")
        try:
            self.fonts = {size: pygame.font.Font(str(font_path), size)
                          for size in (13, 15, 17, 20, 26, 32)}
        except (OSError, pygame.error):
            self.asset_notice = "한글 폰트 경로를 확인하세요: assets/fonts/NotoSansCJKkr-Regular.otf"
            self.fonts = {size: pygame.font.SysFont("malgungothic,applesdgothicneo,notosanscjkkr", size)
                          for size in (13, 15, 17, 20, 26, 32)}
        self.images = {}
        for name in ("grass", "path", "tree", "house", "hero"):
            try:
                source = pygame.image.load(str(assets / f"{name}.png")).convert_alpha()
                self.images[name] = pygame.transform.scale(source, (TILE, TILE))
            except (OSError, pygame.error):
                self.asset_notice = f"{name}.png 로딩 실패: config.json의 assets_dir 경로를 확인하세요."
        self.buttons = {
            "username": pygame.Rect(24, 96, 220, 40),
            "password": pygame.Rect(256, 96, 220, 40),
            "login": pygame.Rect(488, 96, 118, 40),
            "logout": pygame.Rect(618, 96, 118, 40),
            "up": pygame.Rect(830, 312, 92, 42),
            "left": pygame.Rect(728, 364, 92, 42),
            "down": pygame.Rect(830, 364, 92, 42),
            "right": pygame.Rect(932, 364, 92, 42),
            "gather": pygame.Rect(710, 418, 166, 42),
            "train": pygame.Rect(888, 418, 166, 42),
            "history": pygame.Rect(894, 494, 160, 32),
            "delivery": pygame.Rect(366, 724, 282, 30),
            "delivery_api": pygame.Rect(904, 578, 144, 28),
            "analytics": pygame.Rect(366, 690, 130, 28),
            "actions": pygame.Rect(508, 690, 140, 28),
            "api_source": pygame.Rect(710, 612, 230, 28),
            "api_up": pygame.Rect(952, 612, 42, 28),
            "api_down": pygame.Rect(1006, 612, 42, 28),
        }
        for panel in self.query_panels.values():
            self.buttons.update(panel.controls())
        self.slots = {
            "village-board": pygame.Rect(24, 656, 310, 78),
            "lobby-banner": pygame.Rect(350, 656, 314, 158),
        }
        self.ad_slots = {
            "village-ad-slot": pygame.Rect(40, 740, 278, 58),
            "lobby-ad-slot": pygame.Rect(710, 788, 342, 24),
        }

    def text(self, text, position, size=17, color=INK):
        self.canvas.blit(self.fonts[size].render(str(text), True, color), position)

    def wrapped(self, text, rect, size=15, color=MUTED):
        font = self.fonts[size]
        line, y = "", rect.y
        for char in str(text):
            if char == "\n" or font.size(line + char)[0] > rect.width:
                self.text(line, (rect.x, y), size, color)
                y += font.get_linesize()
                line = "" if char == "\n" else char
                if y + font.get_linesize() > rect.bottom:
                    return
            else:
                line += char
        self.text(line, (rect.x, y), size, color)

    def card(self, rect, color=WHITE):
        pygame.draw.rect(self.canvas, color, rect, border_radius=12)
        pygame.draw.rect(self.canvas, LINE, rect, 1, border_radius=12)

    def button(self, name, label, enabled=True):
        rect = self.buttons[name]
        pygame.draw.rect(self.canvas, GREEN if enabled else (219, 225, 211), rect, border_radius=8)
        font = self.fonts[17]
        text = font.render(label, True, WHITE if enabled else MUTED)
        self.canvas.blit(text, text.get_rect(center=rect.center))

    def hit_test(self, position):
        size, offset = self.viewport()
        x = (position[0] - offset[0]) * CANVAS[0] / size[0]
        y = (position[1] - offset[1]) * CANVAS[1] / size[1]
        for panel in self.query_panels.values():
            if panel.opened and pygame.Rect(36,162,616,470).collidepoint(x,y):
                return next((key for key, rect in panel.controls().items() if rect.collidepoint(x,y)), None)
        return next((key for key, rect in self.buttons.items()
                     if not key.startswith(("analytics_", "history_", "actions_")) and rect.collidepoint(x, y)), None)

    def viewport(self):
        width, height = self.screen.get_size()
        ratio = min(width / CANVAS[0], height / CANVAS[1])
        size = (max(1, int(CANVAS[0] * ratio)), max(1, int(CANVAS[1] * ratio)))
        return size, ((width - size[0]) // 2, (height - size[1]) // 2)

    def draw(self, state, username, password, focus, fps, *, closing=False):
        assert threading.current_thread() is threading.main_thread()
        self.canvas.fill(CREAM)
        self.text("작은 마을", (24, 19), 32)
        own = state.own or {}
        summary = (f"{own.get('room_id', '방 —')}  |  {state.online_label}  |  "
                   f"내 위치 ({own.get('x', '—')}, {own.get('y', '—')}) · 동전 {own.get('coins', '—')}  |  "
                   f"{PHASES.get(state.phase, state.phase)}")
        summary_image = self.fonts[15].render(summary, True, GREEN if state.ready else MUTED)
        if summary_image.get_width() > 905:
            ratio = 905 / summary_image.get_width()
            summary_image = pygame.transform.smoothscale(summary_image, (905, max(1, int(summary_image.get_height() * ratio))))
        self.canvas.blit(summary_image, (26, 63))
        self.text(f"네트워크 · {PHASES.get(state.phase, state.phase)}", (690, 26), 17,
                  GREEN if state.ready else MUTED)
        self.text(f"화면 FPS  {fps:.0f}", (954, 62), 15, MUTED)

        for name, value, placeholder in (("username", username, "아이디"),
                                          ("password", "•" * len(password), "비밀번호")):
            rect = self.buttons[name]
            self.card(rect)
            if name == focus:
                pygame.draw.rect(self.canvas, GREEN, rect, 2, border_radius=8)
            clip = self.canvas.get_clip()
            self.canvas.set_clip(rect.inflate(-18, -6))
            self.text(value or placeholder, (rect.x + 12, rect.y + 9), 17,
                      INK if value else MUTED)
            self.canvas.set_clip(clip)
        self.button("login", "마을 입장", state.phase == "signed_out" and not closing)
        self.button("logout", "로그아웃", state.own is not None and state.phase != "logging_out" and not closing)
        self.text("방향키 이동 · Space 채집 · X 수련", (756, 108), 15, MUTED)

        draw_world(self, state)

        self.card(pygame.Rect(688, 152, 388, 132))
        self.text("나의 확정 상태", (710, 168), 20)
        own = state.own or {}
        self.text(f"player_id  {own.get('player_id', '—')}", (710, 202), 15)
        self.text(f"room_id  {own.get('room_id', '—')}", (710, 224), 15)
        self.text(f"x  {own.get('x', '—')}   y  {own.get('y', '—')}     coins  {own.get('coins', '—')}     version  {own.get('version', '—')}", (710, 251), 15)
        self.card(pygame.Rect(688, 296, 388, 178))
        enabled = state.ready and state.pending is None and not closing
        for name, label in (("up", "위"), ("left", "왼쪽"), ("down", "아래"), ("right", "오른쪽")):
            self.button(name, label, enabled)
        self.button("gather", "채집 · (2, 2)", enabled)
        self.button("train", "수련 [X] · (3, 2)", enabled and state.has_ws_state and (own.get("x"), own.get("y")) == TRAIN_TILE)

        self.card(pygame.Rect(688, 482, 388, 300))
        self.text("방 접속 현황", (710, 494), 20)
        self.button("history", "조회 중…" if self.history.busy else "내 이력 읽기", state.own is not None and state.phase != "logging_out" and not self.history.busy and not closing)
        self.text(state.online_label, (710, 526), 15, GREEN if state.ready else MUTED)
        self.text("초록 테두리: 나 · 파란 테두리: 다른 사람", (710, 552), 13, MUTED)
        self.text("API 응답" if state.show_delivery_api else "최근 WS 메시지", (710, 581), 15)
        self.button("delivery_api", "WS 메시지 보기" if state.show_delivery_api else "API 응답 보기", not closing)
        if state.show_delivery_api:
            self.button("api_source", {"analytics": "통계 응답", "delivery": "전달 상태 응답", "history": "내 이력 응답", "actions": "행동 통계 응답"}[self.api_source])
            self.button("api_up", "↑")
            self.button("api_down", "↓")
            response = {"analytics": self.analytics.response, "delivery": state.delivery, "history": self.history.response, "actions": self.actions.response}[self.api_source]
            path = "GET /api/analytics/actions/" if self.api_source == "actions" else f"GET /api/{self.api_source}/"
            self.api_scroll = draw_api(self, response, path, self.api_scroll)
        else:
            for index, message in enumerate(state.ws_messages):
                self.wrapped(message, pygame.Rect(710, 609 + index * 38, 342, 38), 13, MUTED)
            if not state.ws_messages:
                self.text("마을 연결을 기다리고 있어요.", (710, 612), 13, MUTED)

        for slot_id, rect in self.slots.items():
            self.card(rect)
            title = "마을 게시판" if slot_id == "village-board" else "대기 · 통계"
            self.text(title, (rect.x + 16, rect.y + 12), 15, MUTED)
            if slot_id == "village-board":
                self.text("소식 준비 중", (rect.x + 16, rect.y + 38), 20)
            else:
                self.button("analytics", "조회 중…" if self.analytics.busy else "통계 읽기", state.own is not None and state.phase != "logging_out" and not self.analytics.busy and not closing)
                self.button("actions", "조회 중…" if self.actions.busy else "행동 통계", state.own is not None and state.phase != "logging_out" and not self.actions.busy and not closing)
                self.button("delivery", "조회 중…" if state.delivery_busy else "내 이벤트 전달 상태", state.can_query_delivery() and not closing)
                result = state.delivery or {}
                values = result.get("json") or {}
                self.text(f"내 이벤트 {values.get('event_count', '—')} · 미발행 {values.get('pending_publish_count', '—')}", (366, 758), 13)
                self.text(f"source: {values.get('source', '—')}", (366, 779), 13, MUTED)
                # The full delivery message is shown in the main status line on response.
        for rect in self.ad_slots.values():
            pygame.draw.rect(self.canvas, CREAM, rect, border_radius=6)
            pygame.draw.rect(self.canvas, LINE, rect, width=1, border_radius=6)
        for panel in self.query_panels.values():
            panel.draw(self)
        self.wrapped("연결을 정리하는 중…" if closing else (self.asset_notice or state.message),
                     pygame.Rect(24, 820, 1048, 43), 15, GREEN)
        size, offset = self.viewport()
        self.screen.fill((223, 228, 211))
        # Keep text at native resolution normally; filter fractional resizing.
        frame = self.canvas if size == CANVAS else pygame.transform.smoothscale(self.canvas, size)
        self.screen.blit(frame, offset)
        pygame.display.flip()
