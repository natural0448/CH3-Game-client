# render.py

## 계층과 책임

화면 조립 — 폰트·에셋·레이아웃·hit test를 소유하고 world와 패널의 draw를 호출한다. 네트워크 요청을 하지 않는다.

원문: `Game-client/render.py`. 호출 경계는 아래 직접 의존성까지만 기술합니다.

## 직접 의존성

```text
from actions_panel import ActionsPanel
from panels import AnalyticsPanel, HistoryPanel, draw_api
from pathlib import Path
from state import GATHER_TILE, TRAIN_TILE, HEIGHT, TILE, WIDTH
from world import draw_world
import json
import pygame
import threading
```

## 변수·상수와 출처

인스턴스/지역 변수는 각 함수 의사코드의 설정식이 출처입니다. 필드 갱신은 해당 메서드 항목에만 기록합니다.

```text
설정 CANVAS ← (1100, 880)
설정 INK ← (33, 53, 49)
설정 MUTED ← (100, 116, 105)
설정 GREEN ← (29, 105, 83)
설정 CREAM ← (245, 244, 234)
설정 WHITE ← (255, 254, 247)
설정 LINE ← (219, 224, 208)
설정 PHASES ← {'signed_out': '로그인 전', 'authenticating': '로그인 확인 중', 'connecting': '첫 상태 대기', 'connected': '마을 연결됨', 'disconnected': '연결 끊김', 'reconnecting': '재연결 중', 'logging_out': '로그아웃 중', 'stopped': '종료됨'}
클래스 Renderer / 기반 없음
```

## Renderer.__init__(self, screen, config=None)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.
- `screen`: 메인 스레드에서 생성한 Pygame display Surface.
- `config`: configuration.load_config()가 읽은 설정 dict.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
검증 threading.current_thread() is threading.main_thread()
설정 self.screen ← screen
설정 self.canvas ← pygame.Surface(CANVAS)
설정 self.analytics ← AnalyticsPanel()
설정 self.history ← HistoryPanel()
설정 self.actions ← ActionsPanel()
설정 self.query_panels ← {'analytics': self.analytics, 'history': self.history, 'actions': self.actions}
설정 self.api_source ← 'delivery'
설정 self.api_scroll ← 0
설정 root ← Path(__file__).resolve().parent
조건 config is None 이면:
  설정 config ← json.loads((root / 'config.json').read_text(encoding='utf-8'))
설정 assets ← root / config.get('assets_dir', 'assets')
설정 self.asset_notice ← ''
설정 font_path ← assets / config.get('font_path', 'fonts/NotoSansCJKkr-Regular.otf')
시도:
  설정 self.fonts ← {size: pygame.font.Font(str(font_path), size) for size in (13, 15, 17, 20, 26, 32)}
예외 (OSError, pygame.error):
  설정 self.asset_notice ← '한글 폰트 경로를 확인하세요: assets/fonts/NotoSansCJKkr-Regular.otf'
  설정 self.fonts ← {size: pygame.font.SysFont('malgungothic,applesdgothicneo,notosanscjkkr', size) for size in (13, 15, 17, 20, 26, 32)}
설정 self.images ← {}
반복 name ← ('grass', 'path', 'tree', 'house', 'hero'):
  시도:
    설정 source ← pygame.image.load(str(assets / f'{name}.png')).convert_alpha()
    설정 self.images[name] ← pygame.transform.scale(source, (TILE, TILE))
  예외 (OSError, pygame.error):
    설정 self.asset_notice ← f'{name}.png 로딩 실패: config.json의 assets_dir 경로를 확인하세요.'
설정 self.buttons ← {'username': pygame.Rect(24, 96, 220, 40), 'password': pygame.Rect(256, 96, 220, 40), 'login': pygame.Rect(488, 96, 118, 40), 'logout': pygame.Rect(618, 96, 118, 40), 'up': pygame.Rect(830, 312, 92, 42), 'left': pygame.Rect(728, 364, 92, 42), 'down': pygame.Rect(830, 364, 92, 42), 'right': pygame.Rect(932, 364, 92, 42), 'gather': pygame.Rect(710, 418, 166, 42), 'train': pygame.Rect(888, 418, 166, 42), 'history': pygame.Rect(894, 494, 160, 32), 'delivery': pygame.Rect(366, 724, 282, 30), 'delivery_api': pygame.Rect(904, 578, 144, 28), 'analytics': pygame.Rect(366, 690, 130, 28), 'actions': pygame.Rect(508, 690, 140, 28), 'api_source': pygame.Rect(710, 612, 230, 28), 'api_up': pygame.Rect(952, 612, 42, 28), 'api_down': pygame.Rect(1006, 612, 42, 28)}
반복 panel ← self.query_panels.values():
  실행 self.buttons.update(panel.controls())
설정 self.slots ← {'village-board': pygame.Rect(24, 656, 310, 78), 'lobby-banner': pygame.Rect(350, 656, 314, 158)}
설정 self.ad_slots ← {'village-ad-slot': pygame.Rect(40, 740, 278, 58), 'lobby-ad-slot': pygame.Rect(710, 788, 342, 24)}
```

직접 호출 (내부 구현을 펼치지 않음):

```text
(root / 'config.json').read_text
ActionsPanel
AnalyticsPanel
HistoryPanel
Path
Path(__file__).resolve
config.get
json.loads
panel.controls
pygame.Rect
pygame.Surface
pygame.font.Font
pygame.font.SysFont
pygame.image.load
pygame.image.load(str(assets / f'{name}.png')).convert_alpha
pygame.transform.scale
self.buttons.update
self.query_panels.values
str
threading.current_thread
threading.main_thread
```

## Renderer.text(self, text, position, size=17, color=INK)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.
- `text`: 호출자가 전달하는 `text`; 값의 사용과 직접 호출 출처는 아래 의사코드에 표시.
- `position`: 화면 또는 캔버스의 (x,y) 좌표.
- `size`: 호출자가 전달하는 `size`; 값의 사용과 직접 호출 출처는 아래 의사코드에 표시.
- `color`: 호출자가 전달하는 `color`; 값의 사용과 직접 호출 출처는 아래 의사코드에 표시.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
실행 self.canvas.blit(self.fonts[size].render(str(text), True, color), position)
```

직접 호출 (내부 구현을 펼치지 않음):

```text
self.canvas.blit
self.fonts[size].render
str
```

## Renderer.wrapped(self, text, rect, size=15, color=MUTED)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.
- `text`: 호출자가 전달하는 `text`; 값의 사용과 직접 호출 출처는 아래 의사코드에 표시.
- `rect`: 호출자가 전달하는 `rect`; 값의 사용과 직접 호출 출처는 아래 의사코드에 표시.
- `size`: 호출자가 전달하는 `size`; 값의 사용과 직접 호출 출처는 아래 의사코드에 표시.
- `color`: 호출자가 전달하는 `color`; 값의 사용과 직접 호출 출처는 아래 의사코드에 표시.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 font ← self.fonts[size]
설정 (line, y) ← ('', rect.y)
반복 char ← str(text):
  조건 char == '\n' or font.size(line + char)[0] > rect.width 이면:
    실행 self.text(line, (rect.x, y), size, color)
    갱신 y += font.get_linesize()
    설정 line ← '' if char == '\n' else char
    조건 y + font.get_linesize() > rect.bottom 이면:
      반환 None
  그 외:
    갱신 line += char
실행 self.text(line, (rect.x, y), size, color)
```

직접 호출 (내부 구현을 펼치지 않음):

```text
font.get_linesize
font.size
self.text
str
```

## Renderer.card(self, rect, color=WHITE)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.
- `rect`: 호출자가 전달하는 `rect`; 값의 사용과 직접 호출 출처는 아래 의사코드에 표시.
- `color`: 호출자가 전달하는 `color`; 값의 사용과 직접 호출 출처는 아래 의사코드에 표시.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
실행 pygame.draw.rect(self.canvas, color, rect, border_radius=12)
실행 pygame.draw.rect(self.canvas, LINE, rect, 1, border_radius=12)
```

직접 호출 (내부 구현을 펼치지 않음):

```text
pygame.draw.rect
```

## Renderer.button(self, name, label, enabled=True)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.
- `name`: 호출자가 전달하는 `name`; 값의 사용과 직접 호출 출처는 아래 의사코드에 표시.
- `label`: 호출자가 전달하는 `label`; 값의 사용과 직접 호출 출처는 아래 의사코드에 표시.
- `enabled`: 호출자가 전달하는 `enabled`; 값의 사용과 직접 호출 출처는 아래 의사코드에 표시.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 rect ← self.buttons[name]
실행 pygame.draw.rect(self.canvas, GREEN if enabled else (219, 225, 211), rect, border_radius=8)
설정 font ← self.fonts[17]
설정 text ← font.render(label, True, WHITE if enabled else MUTED)
실행 self.canvas.blit(text, text.get_rect(center=rect.center))
```

직접 호출 (내부 구현을 펼치지 않음):

```text
font.render
pygame.draw.rect
self.canvas.blit
text.get_rect
```

## Renderer.hit_test(self, position)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.
- `position`: 화면 또는 캔버스의 (x,y) 좌표.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 (size, offset) ← self.viewport()
설정 x ← (position[0] - offset[0]) * CANVAS[0] / size[0]
설정 y ← (position[1] - offset[1]) * CANVAS[1] / size[1]
반복 panel ← self.query_panels.values():
  조건 panel.opened and pygame.Rect(36, 162, 616, 470).collidepoint(x, y) 이면:
    반환 next((key for key, rect in panel.controls().items() if rect.collidepoint(x, y)), None)
반환 next((key for key, rect in self.buttons.items() if not key.startswith(('analytics_', 'history_', 'actions_')) and rect.collidepoint(x, y)), None)
```

직접 호출 (내부 구현을 펼치지 않음):

```text
key.startswith
next
panel.controls
panel.controls().items
pygame.Rect
pygame.Rect(36, 162, 616, 470).collidepoint
rect.collidepoint
self.buttons.items
self.query_panels.values
self.viewport
```

## Renderer.viewport(self)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 (width, height) ← self.screen.get_size()
설정 ratio ← min(width / CANVAS[0], height / CANVAS[1])
설정 size ← (max(1, int(CANVAS[0] * ratio)), max(1, int(CANVAS[1] * ratio)))
반환 (size, ((width - size[0]) // 2, (height - size[1]) // 2))
```

직접 호출 (내부 구현을 펼치지 않음):

```text
int
max
min
self.screen.get_size
```

## Renderer.draw(self, state, username, password, focus, fps, *, closing=False)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.
- `state`: 메인 스레드의 VillageState; 서버 확정 정보만 포함.
- `username`: 로그인 입력 문자열; 파일/로그에 저장하지 않음.
- `password`: 로그인 입력 비밀번호; 화면은 마스킹하며 요청 후 참조 제거.
- `focus`: username/password/None 입력 포커스.
- `fps`: 메인 clock.get_fps()의 표시값.
- `closing`: 창 종료 처리 중인지 나타내는 bool.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
검증 threading.current_thread() is threading.main_thread()
실행 self.canvas.fill(CREAM)
실행 self.text('작은 마을', (24, 19), 32)
설정 own ← state.own or {}
설정 summary ← f"{own.get('room_id', '방 —')}  |  {state.online_label}  |  내 위치 ({own.get('x', '—')}, {own.get('y', '—')}) · 동전 {own.get('coins', '—')}  |  {PHASES.get(state.phase, state.phase)}"
설정 summary_image ← self.fonts[15].render(summary, True, GREEN if state.ready else MUTED)
조건 summary_image.get_width() > 905 이면:
  설정 ratio ← 905 / summary_image.get_width()
  설정 summary_image ← pygame.transform.smoothscale(summary_image, (905, max(1, int(summary_image.get_height() * ratio))))
실행 self.canvas.blit(summary_image, (26, 63))
실행 self.text(f'네트워크 · {PHASES.get(state.phase, state.phase)}', (690, 26), 17, GREEN if state.ready else MUTED)
실행 self.text(f'화면 FPS  {fps:.0f}', (954, 62), 15, MUTED)
반복 (name, value, placeholder) ← (('username', username, '아이디'), ('password', '•' * len(password), '비밀번호')):
  설정 rect ← self.buttons[name]
  실행 self.card(rect)
  조건 name == focus 이면:
    실행 pygame.draw.rect(self.canvas, GREEN, rect, 2, border_radius=8)
  설정 clip ← self.canvas.get_clip()
  실행 self.canvas.set_clip(rect.inflate(-18, -6))
  실행 self.text(value or placeholder, (rect.x + 12, rect.y + 9), 17, INK if value else MUTED)
  실행 self.canvas.set_clip(clip)
실행 self.button('login', '마을 입장', state.phase == 'signed_out' and (not closing))
실행 self.button('logout', '로그아웃', state.own is not None and state.phase != 'logging_out' and (not closing))
실행 self.text('방향키 이동 · Space 채집 · X 수련', (756, 108), 15, MUTED)
실행 draw_world(self, state)
실행 self.card(pygame.Rect(688, 152, 388, 132))
실행 self.text('나의 확정 상태', (710, 168), 20)
설정 own ← state.own or {}
실행 self.text(f"player_id  {own.get('player_id', '—')}", (710, 202), 15)
실행 self.text(f"room_id  {own.get('room_id', '—')}", (710, 224), 15)
실행 self.text(f"x  {own.get('x', '—')}   y  {own.get('y', '—')}     coins  {own.get('coins', '—')}     version  {own.get('version', '—')}", (710, 251), 15)
실행 self.card(pygame.Rect(688, 296, 388, 178))
설정 enabled ← state.ready and state.pending is None and (not closing)
반복 (name, label) ← (('up', '위'), ('left', '왼쪽'), ('down', '아래'), ('right', '오른쪽')):
  실행 self.button(name, label, enabled)
실행 self.button('gather', '채집 · (2, 2)', enabled)
실행 self.button('train', '수련 [X] · (3, 2)', enabled and state.has_ws_state and ((own.get('x'), own.get('y')) == TRAIN_TILE))
실행 self.card(pygame.Rect(688, 482, 388, 300))
실행 self.text('방 접속 현황', (710, 494), 20)
실행 self.button('history', '조회 중…' if self.history.busy else '내 이력 읽기', state.own is not None and state.phase != 'logging_out' and (not self.history.busy) and (not closing))
실행 self.text(state.online_label, (710, 526), 15, GREEN if state.ready else MUTED)
실행 self.text('초록 테두리: 나 · 파란 테두리: 다른 사람', (710, 552), 13, MUTED)
실행 self.text('API 응답' if state.show_delivery_api else '최근 WS 메시지', (710, 581), 15)
실행 self.button('delivery_api', 'WS 메시지 보기' if state.show_delivery_api else 'API 응답 보기', not closing)
조건 state.show_delivery_api 이면:
  실행 self.button('api_source', {'analytics': '통계 응답', 'delivery': '전달 상태 응답', 'history': '내 이력 응답', 'actions': '행동 통계 응답'}[self.api_source])
  실행 self.button('api_up', '↑')
  실행 self.button('api_down', '↓')
  설정 response ← {'analytics': self.analytics.response, 'delivery': state.delivery, 'history': self.history.response, 'actions': self.actions.response}[self.api_source]
  설정 path ← 'GET /api/analytics/actions/' if self.api_source == 'actions' else f'GET /api/{self.api_source}/'
  설정 self.api_scroll ← draw_api(self, response, path, self.api_scroll)
그 외:
  반복 (index, message) ← enumerate(state.ws_messages):
    실행 self.wrapped(message, pygame.Rect(710, 609 + index * 38, 342, 38), 13, MUTED)
  조건 not state.ws_messages 이면:
    실행 self.text('마을 연결을 기다리고 있어요.', (710, 612), 13, MUTED)
반복 (slot_id, rect) ← self.slots.items():
  실행 self.card(rect)
  설정 title ← '마을 게시판' if slot_id == 'village-board' else '대기 · 통계'
  실행 self.text(title, (rect.x + 16, rect.y + 12), 15, MUTED)
  조건 slot_id == 'village-board' 이면:
    실행 self.text('소식 준비 중', (rect.x + 16, rect.y + 38), 20)
  그 외:
    실행 self.button('analytics', '조회 중…' if self.analytics.busy else '통계 읽기', state.own is not None and state.phase != 'logging_out' and (not self.analytics.busy) and (not closing))
    실행 self.button('actions', '조회 중…' if self.actions.busy else '행동 통계', state.own is not None and state.phase != 'logging_out' and (not self.actions.busy) and (not closing))
    실행 self.button('delivery', '조회 중…' if state.delivery_busy else '내 이벤트 전달 상태', state.can_query_delivery() and (not closing))
    설정 result ← state.delivery or {}
    설정 values ← result.get('json') or {}
    실행 self.text(f"내 이벤트 {values.get('event_count', '—')} · 미발행 {values.get('pending_publish_count', '—')}", (366, 758), 13)
    실행 self.text(f"source: {values.get('source', '—')}", (366, 779), 13, MUTED)
반복 rect ← self.ad_slots.values():
  실행 pygame.draw.rect(self.canvas, CREAM, rect, border_radius=6)
  실행 pygame.draw.rect(self.canvas, LINE, rect, width=1, border_radius=6)
반복 panel ← self.query_panels.values():
  실행 panel.draw(self)
실행 self.wrapped('연결을 정리하는 중…' if closing else self.asset_notice or state.message, pygame.Rect(24, 820, 1048, 43), 15, GREEN)
설정 (size, offset) ← self.viewport()
실행 self.screen.fill((223, 228, 211))
설정 frame ← self.canvas if size == CANVAS else pygame.transform.smoothscale(self.canvas, size)
실행 self.screen.blit(frame, offset)
실행 pygame.display.flip()
```

직접 호출 (내부 구현을 펼치지 않음):

```text
PHASES.get
draw_api
draw_world
enumerate
int
len
max
own.get
panel.draw
pygame.Rect
pygame.display.flip
pygame.draw.rect
pygame.transform.smoothscale
rect.inflate
result.get
self.ad_slots.values
self.button
self.canvas.blit
self.canvas.fill
self.canvas.get_clip
self.canvas.set_clip
self.card
self.fonts[15].render
self.query_panels.values
self.screen.blit
self.screen.fill
self.slots.items
self.text
self.viewport
self.wrapped
state.can_query_delivery
summary_image.get_height
summary_image.get_width
threading.current_thread
threading.main_thread
values.get
```
