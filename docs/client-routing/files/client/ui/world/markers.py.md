# client/ui/world/markers.py

## 책임

`GATHER_TILE`과 `TRAIN_TILE`의 시각 marker와 문구만 그린다.

## 함수

`draw_markers(painter)` — 32px tile 좌표로 채집 원형과 수련 깃발을 그린다.

직접 호출: `pygame.draw`, `Painter.text`. 보상 계산과 명령 전송은 하지 않는다.
