"""Room membership, recent WS messages and safe API response viewer."""
import pygame

from client.ui.drawing import GREEN, MUTED
from client.ui.panels import draw_api


def draw_activity(painter, app, game, queries):
    painter.card(pygame.Rect(688, 482, 388, 300))
    painter.text("방 접속 현황", (710, 494), 20)
    history = queries["history"]
    enabled = game.own is not None and app.phase != "logging_out" and not history.busy and not app.closing
    painter.button("history", "조회 중…" if history.busy else "내 이력 읽기", enabled)
    painter.text(game.online_label, (710, 526), 15, GREEN if game.ready else MUTED)
    painter.text("초록 테두리: 나 · 파란 테두리: 다른 사람", (710, 552), 13, MUTED)
    painter.text("API 응답" if app.show_api else "최근 WS 메시지", (710, 581), 15)
    painter.button("delivery_api", "WS 메시지 보기" if app.show_api else "API 응답 보기", not app.closing)
    if app.show_api:
        labels = {"analytics": "통계 응답", "delivery": "전달 상태 응답",
                  "history": "내 이력 응답", "actions": "행동 통계 응답",
                  "ingest": "수집 통계 응답", "windows": "시간 창 응답",
                  "load": "수업 측정 응답", "metrics": "분석 전달 응답",
                  "lake": "원본 보존 응답"}
        painter.button("api_source", labels[app.api_source])
        painter.button("api_up", "↑")
        painter.button("api_down", "↓")
        draw_api(painter, queries[app.api_source], app.api_source, app.api_scroll)
    else:
        for index, message in enumerate(app.ws_messages):
            painter.wrapped(message, pygame.Rect(710, 609 + index * 38, 342, 38), 13, MUTED)
        if not app.ws_messages:
            painter.text("마을 연결을 기다리고 있어요.", (710, 612), 13, MUTED)
