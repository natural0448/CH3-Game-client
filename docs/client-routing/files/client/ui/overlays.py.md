# client/ui/overlays.py

## 책임

world 이후의 연결 overlay와 최하단 상태 문구만 그린다.

## 함수

`draw_connection_overlay(painter, game)` — game.ready가 false이면 반투명 world overlay와 첫 state 대기 카드를 그린다.

`draw_status(painter, app, asset_notice)` — closing, asset 오류, application message 중 표시할 문구를 그린다.

직접 호출: `pygame.Surface`, `Painter.card/text/wrapped`.
