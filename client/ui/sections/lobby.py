"""Board, statistics entry points and preserved ad slots."""
import pygame

from client.ui.drawing import CREAM, LINE, MUTED


def draw_lobby(painter, app, game, queries):
    for slot_id, rect in painter.layout.slots.items():
        painter.card(rect)
        title = "마을 게시판" if slot_id == "village-board" else "대기 · 통계"
        painter.text(title, (rect.x + 16, rect.y + 12), 15, MUTED)
        if slot_id == "village-board":
            painter.text("소식 준비 중", (rect.x + 16, rect.y + 38), 20)
            continue
        can_query = game.own is not None and app.phase != "logging_out" and not app.closing
        analytics = queries["analytics"]
        actions = queries["actions"]
        ingest = queries["ingest"]
        windows = queries["windows"]
        delivery = queries["delivery"]
        painter.button("analytics", "조회…" if analytics.busy else "전체", can_query and analytics.can_request)
        painter.button("actions", "조회…" if actions.busy else "행동", can_query and actions.can_request)
        painter.button("ingest", "조회…" if ingest.busy else "수집", can_query and ingest.can_request)
        painter.button("windows", "조회…" if windows.busy else "시간 창", can_query and windows.can_request)
        painter.button("delivery", "조회 중…" if delivery.busy else "내 이벤트 전달 상태", can_query and delivery.can_request)
        result = delivery.response or {}
        values = result.get("json") or {}
        painter.text(f"내 이벤트 {values.get('event_count', '—')} · 미발행 {values.get('pending_publish_count', '—')}", (366, 758), 13)
        painter.text(f"source: {values.get('source', '—')}", (366, 779), 13, MUTED)
    for rect in painter.layout.ad_slots.values():
        pygame.draw.rect(painter.canvas, CREAM, rect, border_radius=6)
        pygame.draw.rect(painter.canvas, LINE, rect, width=1, border_radius=6)
