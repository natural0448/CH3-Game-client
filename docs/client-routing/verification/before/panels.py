"""Main-thread analytics display, separate from authoritative player state."""
import json
import uuid
from dataclasses import dataclass
from datetime import datetime

import pygame


@dataclass
class AnalyticsPanel:
    kind = "analytics"
    opened: bool = False
    busy: bool = False
    response: dict | None = None
    pending: str | None = None
    page: int = 0

    def reset(self):
        self.opened = self.busy = False
        self.response = self.pending = None
        self.page = 0

    def request(self, state):
        if self.busy or state.own is None or state.phase in ("logging_out", "signed_out", "stopped"):
            return None
        self.opened = self.busy = True
        self.pending = str(uuid.uuid4())
        self.page = 0
        return {"kind":self.kind, "request_id":self.pending, "player_id":state.own["player_id"]}

    def accept(self, event, state):
        if event.get("kind") in ("logged_out", "login_failed", "stopped"):
            self.reset()
        elif (event.get("kind") == self.kind and self.pending is not None
              and event.get("request_id") == self.pending and state.own is not None
              and event.get("player_id") == state.own["player_id"] and state.phase != "logging_out"):
            self.response = {key:event[key] for key in ("path", "status", "json", "message")}
            self.busy = False
            self.pending = None

    def controls(self):
        return {
            "analytics_close":pygame.Rect(530, 174, 104, 32),
            "analytics_previous":pygame.Rect(420, 588, 92, 30),
            "analytics_next":pygame.Rect(526, 588, 92, 30),
        }

    def turn_page(self, step):
        data = (self.response or {}).get("json") or {}
        count = max(len(data.get("by_action", [])), len(data.get("by_room", [])))
        self.page = max(0, min(self.page + step, max(0, (count - 1) // 6)))

    def draw(self, renderer):
        if not self.opened:
            return
        renderer.card(pygame.Rect(36, 162, 616, 470))
        renderer.text("대기 · Spark 통계", (56, 179), 20)
        renderer.button("analytics_close", "닫기")
        renderer.text("저장된 집계 조회 · 버튼으로만 갱신", (56, 213), 13)
        if self.busy:
            renderer.text("통계를 읽고 있어요…", (72, 317), 20)
            return
        response = self.response or {}
        data = response.get("json")
        if data is None or not data.get("available"):
            message = response.get("message", "통계 읽기 버튼을 눌러 주세요.")
            renderer.wrapped(message, pygame.Rect(72, 303, 544, 120), 20)
            return
        renderer.text(f"전체 확정 사실  {data['event_count']:,}건", (56, 249), 26)
        stamp = datetime.fromisoformat(data["generated_at"]).isoformat(sep=" ", timespec="seconds")
        renderer.text("집계 생성 시각: " + stamp, (56, 295), 13)
        renderer.text("게임 현재 상태와 집계 시점은 다를 수 있습니다", (56, 565), 13)
        renderer.text("행동별", (56, 334), 17)
        renderer.text("방별", (352, 334), 17)
        for field, key, left in (("by_action", "event_type", 56), ("by_room", "room_id", 352)):
            rows = data[field][self.page * 6:(self.page + 1) * 6]
            if not rows:
                renderer.text("표시할 항목 없음", (left, 373), 15)
            for index, row in enumerate(rows):
                y = 370 + index * 33
                pygame.draw.line(renderer.canvas, (219,224,208), (left, y+29), (left+264, y+29))
                old_clip = renderer.canvas.get_clip()
                renderer.canvas.set_clip(pygame.Rect(left, y, 197, 28))
                renderer.text(row[key], (left, y), 15)
                renderer.canvas.set_clip(old_clip)
                count = renderer.fonts[15].render(str(row["count"]), True, (33,53,49))
                renderer.canvas.blit(count, count.get_rect(topright=(left+264, y)))
        count = max(len(data["by_action"]), len(data["by_room"]))
        pages = max(1, (count + 5)//6)
        renderer.text(f"목록 {self.page+1}/{pages} · 상세 값은 API 응답 보기", (56, 590), 13)
        renderer.button("analytics_previous", "이전", self.page > 0)
        renderer.button("analytics_next", "다음", self.page+1 < pages)


class HistoryPanel(AnalyticsPanel):
    kind = "history"

    def controls(self):
        return {
            "history_close": pygame.Rect(530, 174, 104, 32),
            "history_previous": pygame.Rect(420, 588, 92, 30),
            "history_next": pygame.Rect(526, 588, 92, 30),
        }

    def turn_page(self, step):
        rows = ((self.response or {}).get("json") or {}).get("events", [])
        self.page = max(0, min(self.page + step, max(0, (len(rows) - 1) // 4)))

    def draw(self, renderer):
        if not self.opened:
            return
        renderer.card(pygame.Rect(36, 162, 616, 470))
        renderer.text("내 행동 이력", (56, 179), 20)
        renderer.button("history_close", "닫기")
        renderer.text("내 최근 20개 · 버튼으로만 조회 · 전체 집계 아님", (56, 213), 13)
        response = self.response or {}
        rows = (response.get("json") or {}).get("events", [])
        if self.busy or not rows:
            renderer.wrapped("이력을 읽고 있어요…" if self.busy else response.get("message", "내 이력 읽기를 눌러 주세요."), pygame.Rect(56, 288, 556, 140), 20)
            return
        for index, event in enumerate(rows[self.page * 4:(self.page + 1) * 4]):
            y = 248 + index * 78
            stamp = datetime.fromisoformat(event["event_time"]).astimezone().strftime("%m-%d %H:%M:%S")
            renderer.text(f"{stamp}   {event['event_type']}", (56, y), 15)
            transition = event["payload"].get("transition")
            if transition is None:
                label = "확장 이전 기록 · step/reward — · action 기록 없음"
            else:
                label = f"step {transition['step']}  ·  reward {transition['reward']}  ·  action {transition['action']['type']}"
            renderer.text(label, (56, y + 23), 13)
            renderer.text("event_id: " + event["event_id"], (56, y + 43), 13, (100, 116, 105))
            pygame.draw.line(renderer.canvas, (219, 224, 208), (56, y + 71), (630, y + 71))
        pages = max(1, (len(rows) + 3) // 4)
        renderer.text(f"{self.page + 1}/{pages} 페이지 · 시각은 PC 현지 시간", (56, 591), 13)
        renderer.button("history_previous", "이전", self.page > 0)
        renderer.button("history_next", "다음", self.page + 1 < pages)


def draw_api(renderer, response, path, scroll):
    """Draw only the worker's whitelisted result, with bounded viewport scrolling."""
    response = response or {}
    text = f"{path}\nstatus: {response.get('status') or '—'}\n"
    text += json.dumps(response["json"], ensure_ascii=False, indent=2) if response.get("json") is not None else "조회 결과 없음"
    lines = []
    for line in text.splitlines():
        chunk = ""
        for char in line:
            if renderer.fonts[13].size(chunk + char)[0] > 332:
                lines.append(chunk)
                chunk = ""
            chunk += char
        lines.append(chunk)
    scroll = max(0, min(scroll, max(0, len(lines)-5)))
    clip = renderer.canvas.get_clip()
    renderer.canvas.set_clip(pygame.Rect(710, 647, 342, 124))
    for index, line in enumerate(lines[scroll:scroll+5]):
        renderer.text(line, (710, 647+index*23), 13)
    renderer.canvas.set_clip(clip)
    return scroll
