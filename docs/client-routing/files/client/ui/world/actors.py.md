# client/ui/world/actors.py

## 책임

Projection의 ActorView 목록을 캐릭터 layer에 그린다.

## 함수

`draw_actors(painter, actors)` — shadow, hero/fallback sprite, 내 초록/타인 파란 테두리를 순서대로 그린다.

직접 호출: `pygame.draw`, Surface.blit. player 상태는 변경하지 않는다.
