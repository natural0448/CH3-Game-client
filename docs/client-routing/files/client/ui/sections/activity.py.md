# client/ui/sections/activity.py

## 책임

방 인원, 최근 WS 문구, 이력 버튼과 안전한 API 응답 보기 영역을 그린다.

## 함수

`draw_activity(painter, app, game, queries)`

```text
history QueryView로 버튼 상태 표시
GameView.online_label 표시
show_api면 source/up/down과 panels.draw_api 호출
아니면 최근 WS 문구 최대 3개 표시
```

직접 호출: `Painter`, `draw_api`, `pygame.Rect`.
