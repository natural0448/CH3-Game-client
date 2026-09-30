# client/ui/sections/lobby.py

## 책임

마을 게시판, 조회 진입 버튼, delivery 요약과 기존 광고 slot을 그린다.

## 함수

`draw_lobby(painter, app, game, queries)` — village-board/lobby-banner, QueryView.can_request를 반영한 analytics/actions/ingest/windows/load/metrics/delivery/lake 버튼과 event_count/pending/source를 표시하며 광고 slot은 빈 영역으로 유지한다. lake는 "원본 보존" 진입 버튼이며 busy이면 "조회…"를 표시한다. GET은 호출하지 않고 InputRouter가 클릭 intent를 만든다.

직접 호출: `Painter.card/text/button`, `pygame.draw.rect`. GET이나 게임 상태 변경은 하지 않는다.
