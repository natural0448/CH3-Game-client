# client/ui/sections/lobby.py

## 책임

마을 게시판, 조회 진입 버튼, delivery 요약과 기존 광고 slot을 그린다.

## 함수

`draw_lobby(painter, app, game, queries)` — village-board/lobby-banner, QueryView.can_request를 반영한 analytics/actions/ingest/windows/delivery 버튼과 event_count/pending/source를 표시하며 광고 slot은 빈 영역으로 유지한다. windows 버튼은 사용자가 눌렀을 때만 조회 intent를 시작한다.

직접 호출: `Painter.card/text/button`, `pygame.draw.rect`. GET이나 게임 상태 변경은 하지 않는다.
