# client/ui/sections/commands.py

## 책임

내 서버 확정 상태와 방향·채집·수련 control을 그린다.

## 함수

`draw_commands(painter, app, game)` — own player/room/x/y/coins/version을 표시하고 ready·pending·closing으로 버튼을 제어하며 수련은 `TRAIN_TILE`에서만 활성화한다.

직접 호출: `Painter.card/text/button`, `pygame.Rect`.
