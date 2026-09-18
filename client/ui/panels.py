"""Stateless read-only query panels."""
import json
from datetime import datetime

import pygame

from client.contracts.queries import ACTION_TYPES, QUERY_SPECS
from client.ui.drawing import INK, LINE, MUTED


def draw_analytics(painter, slot):
    if not slot.opened:
        return
    painter.card(painter.layout.panel_rect)
    painter.text("대기 · Spark 통계", (56, 179), 20)
    painter.button("analytics_close", "닫기")
    painter.text("저장된 집계 조회 · 버튼으로만 갱신", (56, 213), 13)
    if slot.busy:
        painter.text("통계를 읽고 있어요…", (72, 317), 20)
        return
    response = slot.response or {}
    data = response.get("json")
    if data is None or not data.get("available"):
        painter.wrapped(response.get("message", "통계 읽기 버튼을 눌러 주세요."), pygame.Rect(72, 303, 544, 120), 20)
        return
    painter.text(f"전체 확정 사실  {data['event_count']:,}건", (56, 249), 26)
    stamp = datetime.fromisoformat(data["generated_at"]).isoformat(sep=" ", timespec="seconds")
    painter.text("집계 생성 시각: " + stamp, (56, 295), 13)
    painter.text("게임 현재 상태와 집계 시점은 다를 수 있습니다", (56, 565), 13)
    painter.text("행동별", (56, 334), 17)
    painter.text("방별", (352, 334), 17)
    for field, key, left in (("by_action", "event_type", 56), ("by_room", "room_id", 352)):
        rows = data[field][slot.page * 6:(slot.page + 1) * 6]
        if not rows:
            painter.text("표시할 항목 없음", (left, 373), 15)
        for index, row in enumerate(rows):
            y = 370 + index * 33
            pygame.draw.line(painter.canvas, LINE, (left, y + 29), (left + 264, y + 29))
            old_clip = painter.canvas.get_clip()
            painter.canvas.set_clip(pygame.Rect(left, y, 197, 28))
            painter.text(row[key], (left, y), 15)
            painter.canvas.set_clip(old_clip)
            count = painter.fonts[15].render(str(row["count"]), True, INK)
            painter.canvas.blit(count, count.get_rect(topright=(left + 264, y)))
    count = max(len(data["by_action"]), len(data["by_room"]))
    pages = max(1, (count + 5) // 6)
    painter.text(f"목록 {slot.page + 1}/{pages} · 상세 값은 API 응답 보기", (56, 590), 13)
    painter.button("analytics_previous", "이전", slot.page > 0)
    painter.button("analytics_next", "다음", slot.page + 1 < pages)


def draw_history(painter, slot):
    if not slot.opened:
        return
    painter.card(painter.layout.panel_rect)
    painter.text("내 행동 이력", (56, 179), 20)
    painter.button("history_close", "닫기")
    painter.text("내 최근 20개 · 버튼으로만 조회 · 전체 집계 아님", (56, 213), 13)
    response = slot.response or {}
    rows = (response.get("json") or {}).get("events", [])
    if slot.busy or not rows:
        painter.wrapped("이력을 읽고 있어요…" if slot.busy else response.get("message", "내 이력 읽기를 눌러 주세요."),
                        pygame.Rect(56, 288, 556, 140), 20)
        return
    for index, event in enumerate(rows[slot.page * 4:(slot.page + 1) * 4]):
        y = 248 + index * 78
        stamp = datetime.fromisoformat(event["event_time"]).astimezone().strftime("%m-%d %H:%M:%S")
        painter.text(f"{stamp}   {event['event_type']}", (56, y), 15)
        transition = event["payload"].get("transition")
        label = ("확장 이전 기록 · step/reward — · action 기록 없음" if transition is None else
                 f"step {transition['step']}  ·  reward {transition['reward']}  ·  action {transition['action']['type']}")
        painter.text(label, (56, y + 23), 13)
        painter.text("event_id: " + event["event_id"], (56, y + 43), 13, MUTED)
        pygame.draw.line(painter.canvas, LINE, (56, y + 71), (630, y + 71))
    pages = max(1, (len(rows) + 3) // 4)
    painter.text(f"{slot.page + 1}/{pages} 페이지 · 시각은 PC 현지 시간", (56, 591), 13)
    painter.button("history_previous", "이전", slot.page > 0)
    painter.button("history_next", "다음", slot.page + 1 < pages)


def draw_actions(painter, slot):
    if not slot.opened:
        return
    painter.card(painter.layout.panel_rect)
    painter.text("행동 통계", (56, 177), 20)
    painter.button("actions_refresh", "조회 중…" if slot.busy else "다시 조회", not slot.busy)
    painter.button("actions_close", "닫기")
    painter.text("고정 snapshot · 마지막 집계 기준", (56, 215), 15)
    data = (slot.response or {}).get("json")
    if slot.busy or data is None or not data.get("available"):
        if slot.busy:
            message = "행동 통계를 읽고 있어요…"
        elif data is not None and data.get("available") is False:
            message = "행동 집계가 아직 없습니다"
        else:
            message = (slot.response or {}).get("message", "조회 버튼을 눌러 주세요.")
        painter.wrapped(message, pygame.Rect(56, 296, 556, 140), 20)
        return
    summary = data["summary"]
    painter.text("source_topic: " + data["source_topic"], (56, 243), 13)
    painter.text("source_kind: " + data["source_kind"], (56, 264), 13)
    stamp = datetime.fromisoformat(summary["generated_at"]).astimezone().isoformat(sep=" ", timespec="seconds")
    painter.text("집계 생성 시각: " + stamp, (56, 285), 13)
    painter.wrapped(f"고유 행동 수  {summary['event_count']:,}건", pygame.Rect(56, 312, 290, 36), 20)
    painter.wrapped(f"원본 전달 행 수  {data['raw_record_count']:,}행", pygame.Rect(354, 316, 276, 32), 15)
    by_type = {row["event_type"]: row for row in summary["by_action"]}
    for index, event_type in enumerate(ACTION_TYPES):
        left = 56 + index * 194
        rect = pygame.Rect(left, 353, 184, 73)
        painter.card(rect, (235, 241, 229))
        row = by_type.get(event_type)
        painter.wrapped(row["action_label"] if row else "해당 행동 항목 없음", pygame.Rect(left + 10, 360, 164, 23), 15)
        painter.wrapped(f"{row['count']:,}건" if row else "—", pygame.Rect(left + 10, 389, 164, 28), 20)
    painter.text("방별 행동 수", (56, 437), 15)
    rows = summary["by_room"]
    if not rows:
        painter.text("표시할 방 항목 없음", (56, 463), 13)
    for index, row in enumerate(rows[slot.page * 4:(slot.page + 1) * 4]):
        y = 461 + index * 23
        painter.wrapped(row["room_id"], pygame.Rect(56, y, 420, 23), 13)
        painter.wrapped(f"{row['count']:,}건", pygame.Rect(500, y, 130, 23), 13)
    painter.text("접속자 수·잔액이 아니며, 현재 화면의 이동 횟수와 다를 수 있습니다.", (56, 561), 13)
    pages = max(1, (len(rows) + 3) // 4)
    painter.text(f"방 목록 {slot.page + 1}/{pages}", (56, 592), 13)
    painter.button("actions_previous", "이전", slot.page > 0)
    painter.button("actions_next", "다음", slot.page + 1 < pages)


def draw_api(painter, slot, kind, scroll):
    response = slot.response or {}
    text = f"GET {QUERY_SPECS[kind].path}\nstatus: {response.get('status') or '—'}\n"
    text += json.dumps(response["json"], ensure_ascii=False, indent=2) if response.get("json") is not None else "조회 결과 없음"
    lines = []
    for line in text.splitlines():
        chunk = ""
        for char in line:
            if painter.fonts[13].size(chunk + char)[0] > 332:
                lines.append(chunk)
                chunk = ""
            chunk += char
        lines.append(chunk)
    scroll = max(0, min(scroll, max(0, len(lines) - 5)))
    clip = painter.canvas.get_clip()
    painter.canvas.set_clip(pygame.Rect(710, 647, 342, 124))
    for index, line in enumerate(lines[scroll:scroll + 5]):
        painter.text(line, (710, 647 + index * 23), 13)
    painter.canvas.set_clip(clip)


def draw_query_panels(painter, queries):
    draw_analytics(painter, queries["analytics"])
    draw_history(painter, queries["history"])
    draw_actions(painter, queries["actions"])
