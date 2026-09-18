# client/ui/world/terrain.py

## 책임

잔디·길과 장식 배경만 그린다. 충돌·보상 규칙은 없다.

## 함수

`draw_terrain(painter)` — 20×15 tile의 길/잔디 색과 선택 로컬 image를 그린다.

`draw_decorations(painter)` — 고정 위치의 tree/house 이미지와 지붕 장식을 그린다.

직접 호출: `pygame.draw`, Surface.blit, `Painter.images`.
