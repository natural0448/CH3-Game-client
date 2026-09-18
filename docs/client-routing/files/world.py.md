# world.py

## 계층과 책임

마을 표시 — 전달받은 확정 상태와 로컬 CC0 에셋만 그린다. 위치·보상·버전을 계산하지 않는다.

원문: `Game-client/world.py`. 호출 경계는 아래 직접 의존성까지만 기술합니다.

## 직접 의존성

```text
from state import GATHER_TILE, TRAIN_TILE, WIDTH, HEIGHT, TILE
import pygame
```

## 변수·상수와 출처

인스턴스/지역 변수는 각 함수 의사코드의 설정식이 출처입니다. 필드 갱신은 해당 메서드 항목에만 기록합니다.

```text
설정 GREEN ← (29, 105, 83)
설정 INK ← (33, 53, 49)
설정 WHITE ← (255, 254, 247)
```

## draw_world(renderer, state)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `renderer`: 메인 스레드 Renderer; canvas/fonts 및 text/card/button 인터페이스.
- `state`: 메인 스레드의 VillageState; 서버 확정 정보만 포함.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
실행 renderer.card(pygame.Rect(22, 150, 644, 484))
반복 y ← range(HEIGHT):
  반복 x ← range(WIDTH):
    설정 color ← (183, 205, 153) if (x + y) % 2 else (189, 210, 159)
    조건 x == 2 or y == 2 이면:
      설정 color ← (216, 202, 158)
    실행 pygame.draw.rect(renderer.canvas, color, (24 + x * TILE, 152 + y * TILE, TILE, TILE))
    설정 tile ← renderer.images.get('path' if x == 2 or y == 2 else 'grass')
    조건 tile 이면:
      실행 renderer.canvas.blit(tile, (24 + x * TILE, 152 + y * TILE))
조건 'tree' in renderer.images 이면:
  반복 (x, y) ← ((5, 5), (6, 8), (12, 4), (16, 5), (16, 11), (9, 12)):
    실행 renderer.canvas.blit(renderer.images['tree'], (24 + x * TILE, 152 + y * TILE))
조건 'house' in renderer.images 이면:
  반복 (x, y) ← ((7, 5), (13, 9)):
    설정 (px, py) ← (24 + x * TILE, 152 + y * TILE)
    실행 pygame.draw.polygon(renderer.canvas, (155, 73, 61), ((px - 6, py), (px + 16, py - 22), (px + 38, py)))
    실행 renderer.canvas.blit(renderer.images['house'], (px, py))
설정 (gx, gy) ← (24 + GATHER_TILE[0] * TILE, 152 + GATHER_TILE[1] * TILE)
실행 pygame.draw.rect(renderer.canvas, (237, 193, 76), (gx + 2, gy + 2, 28, 28), border_radius=6)
실행 pygame.draw.circle(renderer.canvas, (105, 125, 44), (gx + 16, gy + 17), 9)
실행 pygame.draw.circle(renderer.canvas, (247, 224, 124), (gx + 16, gy + 12), 5)
실행 renderer.text('채집 (2, 2)', (gx - 12, gy + 34), 13)
설정 (tx, ty) ← (24 + TRAIN_TILE[0] * TILE, 152 + TRAIN_TILE[1] * TILE)
실행 pygame.draw.rect(renderer.canvas, (166, 191, 221), (tx + 2, ty + 2, 28, 28), border_radius=6)
실행 pygame.draw.line(renderer.canvas, (63, 82, 132), (tx + 16, ty + 25), (tx + 16, ty + 6), 3)
실행 pygame.draw.polygon(renderer.canvas, (63, 82, 132), [(tx + 16, ty + 5), (tx + 28, ty + 9), (tx + 16, ty + 14)])
실행 renderer.text('개인 수련 (3, 2)', (tx + 36, ty + 4), 13)
조건 state.own is not None and state.has_ws_state 이면:
  설정 occupants ← {}
  반복 player ← sorted(state.players.values(), key=lambda p: (p['y'], p['player_id'] == state.own['player_id'], p['player_id'])):
    실행 occupants.setdefault((player['x'], player['y']), []).append(player['player_id'])
    설정 (x, y) ← (24 + player['x'] * TILE, 152 + player['y'] * TILE)
    설정 mine ← player['player_id'] == state.own['player_id']
    실행 pygame.draw.ellipse(renderer.canvas, (128, 153, 112), (x + 4, y + 23, 25, 7))
    조건 'hero' in renderer.images 이면:
      설정 hero ← renderer.images['hero']
      실행 renderer.canvas.blit(hero, hero.get_rect(midbottom=(x + TILE // 2, y + TILE)))
    그 외:
      실행 pygame.draw.rect(renderer.canvas, GREEN, (x + 7, y + 12, 18, 16), border_radius=5)
      실행 pygame.draw.circle(renderer.canvas, (255, 227, 185), (x + 16, y + 9), 7)
      실행 pygame.draw.circle(renderer.canvas, INK, (x + 19, y + 9), 1)
    실행 pygame.draw.rect(renderer.canvas, GREEN if mine else (78, 95, 171), (x + 1, y + 1, 30, 30), 2, border_radius=5)
  반복 ((tile_x, tile_y), ids) ← occupants.items():
    설정 label ← ', '.join((state.players[pid].get('username') or f'#{pid}' for pid in ids[:3]))
    조건 len(ids) > 3 이면:
      갱신 label += f' +{len(ids) - 3}'
    조건 len(ids) > 1 이면:
      갱신 label += f' ({len(ids)}명)'
    설정 text ← renderer.fonts[13].render(label, True, INK)
    설정 max_height ← 11 if tile_y == 0 else text.get_height()
    설정 scale ← min(1, 636 / max(1, text.get_width()), max_height / text.get_height())
    조건 scale < 1 이면:
      설정 text ← pygame.transform.smoothscale(text, (max(1, int(text.get_width() * scale)), max(1, int(text.get_height() * scale))))
    설정 rect ← text.get_rect(midbottom=(24 + tile_x * TILE + TILE // 2, 152 + tile_y * TILE - 3))
    설정 rect.x ← max(26, min(rect.x, 662 - rect.width))
    실행 pygame.draw.rect(renderer.canvas, WHITE, rect.inflate(4, 2), border_radius=3)
    실행 renderer.canvas.blit(text, rect)
조건 not state.ready 이면:
  설정 overlay ← pygame.Surface((640, 480), pygame.SRCALPHA)
  실행 overlay.fill((244, 245, 232, 140))
  실행 renderer.canvas.blit(overlay, (24, 152))
  실행 renderer.card(pygame.Rect(144, 348, 400, 72))
  실행 renderer.text('서버의 확정 상태를 기다리고 있어요', (180, 371), 20)
```

직접 호출 (내부 구현을 펼치지 않음):

```text
', '.join
hero.get_rect
int
len
max
min
occupants.items
occupants.setdefault
occupants.setdefault((player['x'], player['y']), []).append
overlay.fill
pygame.Rect
pygame.Surface
pygame.draw.circle
pygame.draw.ellipse
pygame.draw.line
pygame.draw.polygon
pygame.draw.rect
pygame.transform.smoothscale
range
rect.inflate
renderer.canvas.blit
renderer.card
renderer.fonts[13].render
renderer.images.get
renderer.text
sorted
state.players.values
state.players[pid].get
text.get_height
text.get_rect
text.get_width
```
