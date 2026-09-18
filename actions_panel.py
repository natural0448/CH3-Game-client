"""Main-thread view of a fixed action snapshot; no computation or HTTP here."""
from datetime import datetime

import pygame

from analytics_data import ACTION_TYPES
from panel_state import QueryPanel


class ActionsPanel(QueryPanel):
    kind = "actions"

    def controls(self):
        return {
            "actions_refresh": pygame.Rect(420, 174, 100, 32),
            "actions_close": pygame.Rect(530, 174, 104, 32),
            "actions_previous": pygame.Rect(420, 588, 92, 30),
            "actions_next": pygame.Rect(526, 588, 92, 30),
        }

    def turn_page(self, step):
        summary = ((self.response or {}).get("json") or {}).get("summary") or {}
        count = len(summary.get("by_room", []))
        self.page = max(0, min(self.page + step, max(0, (count - 1) // 4)))

    def draw(self, renderer):
        if not self.opened:
            return
        renderer.card(pygame.Rect(36, 162, 616, 470))
        renderer.text("행동 통계", (56, 177), 20)
        renderer.button("actions_refresh", "조회 중…" if self.busy else "다시 조회", not self.busy)
        renderer.button("actions_close", "닫기")
        renderer.text("고정 snapshot · 마지막 집계 기준", (56, 215), 15)
        data = (self.response or {}).get("json")
        if self.busy or data is None or not data.get("available"):
            if self.busy:
                message = "행동 통계를 읽고 있어요…"
            elif data is not None and data.get("available") is False:
                message = "행동 집계가 아직 없습니다"
            else:
                message = (self.response or {}).get("message", "조회 버튼을 눌러 주세요.")
            renderer.wrapped(message, pygame.Rect(56, 296, 556, 140), 20)
            return
        summary = data["summary"]
        renderer.text("source_topic: " + data["source_topic"], (56, 243), 13)
        renderer.text("source_kind: " + data["source_kind"], (56, 264), 13)
        stamp = datetime.fromisoformat(summary["generated_at"]).astimezone().isoformat(sep=" ", timespec="seconds")
        renderer.text("집계 생성 시각: " + stamp, (56, 285), 13)
        renderer.wrapped(f"고유 행동 수  {summary['event_count']:,}건", pygame.Rect(56, 312, 290, 36), 20)
        renderer.wrapped(f"원본 전달 행 수  {data['raw_record_count']:,}행", pygame.Rect(354, 316, 276, 32), 15)
        by_type = {row["event_type"]: row for row in summary["by_action"]}
        for index, event_type in enumerate(ACTION_TYPES):
            left = 56 + index * 194
            rect = pygame.Rect(left, 353, 184, 73)
            renderer.card(rect, (235, 241, 229))
            row = by_type.get(event_type)
            label = row["action_label"] if row else "해당 행동 항목 없음"
            renderer.wrapped(label, pygame.Rect(left + 10, 360, 164, 23), 15)
            renderer.wrapped(f"{row['count']:,}건" if row else "—", pygame.Rect(left + 10, 389, 164, 28), 20)
        renderer.text("방별 행동 수", (56, 437), 15)
        rows = summary["by_room"]
        if not rows:
            renderer.text("표시할 방 항목 없음", (56, 463), 13)
        for index, row in enumerate(rows[self.page * 4:(self.page + 1) * 4]):
            y = 461 + index * 23
            renderer.wrapped(row["room_id"], pygame.Rect(56, y, 420, 23), 13)
            renderer.wrapped(f"{row['count']:,}건", pygame.Rect(500, y, 130, 23), 13)
        renderer.text("접속자 수·잔액이 아니며, 현재 화면의 이동 횟수와 다를 수 있습니다.", (56, 561), 13)
        pages = max(1, (len(rows) + 3) // 4)
        renderer.text(f"방 목록 {self.page + 1}/{pages}", (56, 592), 13)
        renderer.button("actions_previous", "이전", self.page > 0)
        renderer.button("actions_next", "다음", self.page + 1 < pages)
