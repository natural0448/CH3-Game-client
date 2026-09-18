# panels.py

## 계층과 책임

조회 표시 — 기존 전체 집계·개인 이력·허용된 API 응답을 그린다. 조회 요청은 상위 app에 맡긴다.

원문: `Game-client/panels.py`. 호출 경계는 아래 직접 의존성까지만 기술합니다.

## 직접 의존성

```text
from datetime import datetime
from panel_state import QueryPanel
import json
import pygame
```

## 변수·상수와 출처

인스턴스/지역 변수는 각 함수 의사코드의 설정식이 출처입니다. 필드 갱신은 해당 메서드 항목에만 기록합니다.

```text
클래스 AnalyticsPanel / 기반 QueryPanel
  설정 kind ← 'analytics'
클래스 HistoryPanel / 기반 QueryPanel
  설정 kind ← 'history'
```

## AnalyticsPanel.controls(self)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
반환 {'analytics_close': pygame.Rect(530, 174, 104, 32), 'analytics_previous': pygame.Rect(420, 588, 92, 30), 'analytics_next': pygame.Rect(526, 588, 92, 30)}
```

직접 호출 (내부 구현을 펼치지 않음):

```text
pygame.Rect
```

## AnalyticsPanel.turn_page(self, step)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.
- `step`: 페이지 이동량; 이전 -1, 다음 +1.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 data ← (self.response or {}).get('json') or {}
설정 count ← max(len(data.get('by_action', [])), len(data.get('by_room', [])))
설정 self.page ← max(0, min(self.page + step, max(0, (count - 1) // 6)))
```

직접 호출 (내부 구현을 펼치지 않음):

```text
(self.response or {}).get
data.get
len
max
min
```

## AnalyticsPanel.draw(self, renderer)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.
- `renderer`: 메인 스레드 Renderer; canvas/fonts 및 text/card/button 인터페이스.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
조건 not self.opened 이면:
  반환 None
실행 renderer.card(pygame.Rect(36, 162, 616, 470))
실행 renderer.text('대기 · Spark 통계', (56, 179), 20)
실행 renderer.button('analytics_close', '닫기')
실행 renderer.text('저장된 집계 조회 · 버튼으로만 갱신', (56, 213), 13)
조건 self.busy 이면:
  실행 renderer.text('통계를 읽고 있어요…', (72, 317), 20)
  반환 None
설정 response ← self.response or {}
설정 data ← response.get('json')
조건 data is None or not data.get('available') 이면:
  설정 message ← response.get('message', '통계 읽기 버튼을 눌러 주세요.')
  실행 renderer.wrapped(message, pygame.Rect(72, 303, 544, 120), 20)
  반환 None
실행 renderer.text(f"전체 확정 사실  {data['event_count']:,}건", (56, 249), 26)
설정 stamp ← datetime.fromisoformat(data['generated_at']).isoformat(sep=' ', timespec='seconds')
실행 renderer.text('집계 생성 시각: ' + stamp, (56, 295), 13)
실행 renderer.text('게임 현재 상태와 집계 시점은 다를 수 있습니다', (56, 565), 13)
실행 renderer.text('행동별', (56, 334), 17)
실행 renderer.text('방별', (352, 334), 17)
반복 (field, key, left) ← (('by_action', 'event_type', 56), ('by_room', 'room_id', 352)):
  설정 rows ← data[field][self.page * 6:(self.page + 1) * 6]
  조건 not rows 이면:
    실행 renderer.text('표시할 항목 없음', (left, 373), 15)
  반복 (index, row) ← enumerate(rows):
    설정 y ← 370 + index * 33
    실행 pygame.draw.line(renderer.canvas, (219, 224, 208), (left, y + 29), (left + 264, y + 29))
    설정 old_clip ← renderer.canvas.get_clip()
    실행 renderer.canvas.set_clip(pygame.Rect(left, y, 197, 28))
    실행 renderer.text(row[key], (left, y), 15)
    실행 renderer.canvas.set_clip(old_clip)
    설정 count ← renderer.fonts[15].render(str(row['count']), True, (33, 53, 49))
    실행 renderer.canvas.blit(count, count.get_rect(topright=(left + 264, y)))
설정 count ← max(len(data['by_action']), len(data['by_room']))
설정 pages ← max(1, (count + 5) // 6)
실행 renderer.text(f'목록 {self.page + 1}/{pages} · 상세 값은 API 응답 보기', (56, 590), 13)
실행 renderer.button('analytics_previous', '이전', self.page > 0)
실행 renderer.button('analytics_next', '다음', self.page + 1 < pages)
```

직접 호출 (내부 구현을 펼치지 않음):

```text
count.get_rect
data.get
datetime.fromisoformat
datetime.fromisoformat(data['generated_at']).isoformat
enumerate
len
max
pygame.Rect
pygame.draw.line
renderer.button
renderer.canvas.blit
renderer.canvas.get_clip
renderer.canvas.set_clip
renderer.card
renderer.fonts[15].render
renderer.text
renderer.wrapped
response.get
str
```

## HistoryPanel.controls(self)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
반환 {'history_close': pygame.Rect(530, 174, 104, 32), 'history_previous': pygame.Rect(420, 588, 92, 30), 'history_next': pygame.Rect(526, 588, 92, 30)}
```

직접 호출 (내부 구현을 펼치지 않음):

```text
pygame.Rect
```

## HistoryPanel.turn_page(self, step)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.
- `step`: 페이지 이동량; 이전 -1, 다음 +1.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 rows ← ((self.response or {}).get('json') or {}).get('events', [])
설정 self.page ← max(0, min(self.page + step, max(0, (len(rows) - 1) // 4)))
```

직접 호출 (내부 구현을 펼치지 않음):

```text
((self.response or {}).get('json') or {}).get
(self.response or {}).get
len
max
min
```

## HistoryPanel.draw(self, renderer)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.
- `renderer`: 메인 스레드 Renderer; canvas/fonts 및 text/card/button 인터페이스.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
조건 not self.opened 이면:
  반환 None
실행 renderer.card(pygame.Rect(36, 162, 616, 470))
실행 renderer.text('내 행동 이력', (56, 179), 20)
실행 renderer.button('history_close', '닫기')
실행 renderer.text('내 최근 20개 · 버튼으로만 조회 · 전체 집계 아님', (56, 213), 13)
설정 response ← self.response or {}
설정 rows ← (response.get('json') or {}).get('events', [])
조건 self.busy or not rows 이면:
  실행 renderer.wrapped('이력을 읽고 있어요…' if self.busy else response.get('message', '내 이력 읽기를 눌러 주세요.'), pygame.Rect(56, 288, 556, 140), 20)
  반환 None
반복 (index, event) ← enumerate(rows[self.page * 4:(self.page + 1) * 4]):
  설정 y ← 248 + index * 78
  설정 stamp ← datetime.fromisoformat(event['event_time']).astimezone().strftime('%m-%d %H:%M:%S')
  실행 renderer.text(f"{stamp}   {event['event_type']}", (56, y), 15)
  설정 transition ← event['payload'].get('transition')
  조건 transition is None 이면:
    설정 label ← '확장 이전 기록 · step/reward — · action 기록 없음'
  그 외:
    설정 label ← f"step {transition['step']}  ·  reward {transition['reward']}  ·  action {transition['action']['type']}"
  실행 renderer.text(label, (56, y + 23), 13)
  실행 renderer.text('event_id: ' + event['event_id'], (56, y + 43), 13, (100, 116, 105))
  실행 pygame.draw.line(renderer.canvas, (219, 224, 208), (56, y + 71), (630, y + 71))
설정 pages ← max(1, (len(rows) + 3) // 4)
실행 renderer.text(f'{self.page + 1}/{pages} 페이지 · 시각은 PC 현지 시간', (56, 591), 13)
실행 renderer.button('history_previous', '이전', self.page > 0)
실행 renderer.button('history_next', '다음', self.page + 1 < pages)
```

직접 호출 (내부 구현을 펼치지 않음):

```text
(response.get('json') or {}).get
datetime.fromisoformat
datetime.fromisoformat(event['event_time']).astimezone
datetime.fromisoformat(event['event_time']).astimezone().strftime
enumerate
event['payload'].get
len
max
pygame.Rect
pygame.draw.line
renderer.button
renderer.card
renderer.text
renderer.wrapped
response.get
```

## draw_api(renderer, response, path, scroll)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `renderer`: 메인 스레드 Renderer; canvas/fonts 및 text/card/button 인터페이스.
- `response`: worker가 허용 목록으로 만든 path/status/json/message dict.
- `path`: 고정 API 경로 또는 호출자가 지정한 로컬 경로.
- `scroll`: API 응답 보기의 첫 표시 줄 위치.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 response ← response or {}
설정 text ← f"{path}\nstatus: {response.get('status') or '—'}\n"
갱신 text += json.dumps(response['json'], ensure_ascii=False, indent=2) if response.get('json') is not None else '조회 결과 없음'
설정 lines ← []
반복 line ← text.splitlines():
  설정 chunk ← ''
  반복 char ← line:
    조건 renderer.fonts[13].size(chunk + char)[0] > 332 이면:
      실행 lines.append(chunk)
      설정 chunk ← ''
    갱신 chunk += char
  실행 lines.append(chunk)
설정 scroll ← max(0, min(scroll, max(0, len(lines) - 5)))
설정 clip ← renderer.canvas.get_clip()
실행 renderer.canvas.set_clip(pygame.Rect(710, 647, 342, 124))
반복 (index, line) ← enumerate(lines[scroll:scroll + 5]):
  실행 renderer.text(line, (710, 647 + index * 23), 13)
실행 renderer.canvas.set_clip(clip)
반환 scroll
```

직접 호출 (내부 구현을 펼치지 않음):

```text
enumerate
json.dumps
len
lines.append
max
min
pygame.Rect
renderer.canvas.get_clip
renderer.canvas.set_clip
renderer.fonts[13].size
renderer.text
response.get
text.splitlines
```
