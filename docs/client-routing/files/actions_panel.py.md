# actions_panel.py

## 계층과 책임

행동 집계 표시 — 고정 snapshot의 메타데이터·세 카드·방별 목록과 미생성/오류를 그린다. GET은 app/network에 맡긴다.

원문: `Game-client/actions_panel.py`. 호출 경계는 아래 직접 의존성까지만 기술합니다.

## 직접 의존성

```text
from analytics_data import ACTION_TYPES
from datetime import datetime
from panel_state import QueryPanel
import pygame
```

## 변수·상수와 출처

인스턴스/지역 변수는 각 함수 의사코드의 설정식이 출처입니다. 필드 갱신은 해당 메서드 항목에만 기록합니다.

```text
클래스 ActionsPanel / 기반 QueryPanel
  설정 kind ← 'actions'
```

## ActionsPanel.controls(self)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
반환 {'actions_refresh': pygame.Rect(420, 174, 100, 32), 'actions_close': pygame.Rect(530, 174, 104, 32), 'actions_previous': pygame.Rect(420, 588, 92, 30), 'actions_next': pygame.Rect(526, 588, 92, 30)}
```

직접 호출 (내부 구현을 펼치지 않음):

```text
pygame.Rect
```

## ActionsPanel.turn_page(self, step)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.
- `step`: 페이지 이동량; 이전 -1, 다음 +1.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 summary ← ((self.response or {}).get('json') or {}).get('summary') or {}
설정 count ← len(summary.get('by_room', []))
설정 self.page ← max(0, min(self.page + step, max(0, (count - 1) // 4)))
```

직접 호출 (내부 구현을 펼치지 않음):

```text
((self.response or {}).get('json') or {}).get
(self.response or {}).get
len
max
min
summary.get
```

## ActionsPanel.draw(self, renderer)

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
실행 renderer.text('행동 통계', (56, 177), 20)
실행 renderer.button('actions_refresh', '조회 중…' if self.busy else '다시 조회', not self.busy)
실행 renderer.button('actions_close', '닫기')
실행 renderer.text('고정 snapshot · 마지막 집계 기준', (56, 215), 15)
설정 data ← (self.response or {}).get('json')
조건 self.busy or data is None or (not data.get('available')) 이면:
  조건 self.busy 이면:
    설정 message ← '행동 통계를 읽고 있어요…'
  그 외:
    조건 data is not None and data.get('available') is False 이면:
      설정 message ← '행동 집계가 아직 없습니다'
    그 외:
      설정 message ← (self.response or {}).get('message', '조회 버튼을 눌러 주세요.')
  실행 renderer.wrapped(message, pygame.Rect(56, 296, 556, 140), 20)
  반환 None
설정 summary ← data['summary']
실행 renderer.text('source_topic: ' + data['source_topic'], (56, 243), 13)
실행 renderer.text('source_kind: ' + data['source_kind'], (56, 264), 13)
설정 stamp ← datetime.fromisoformat(summary['generated_at']).astimezone().isoformat(sep=' ', timespec='seconds')
실행 renderer.text('집계 생성 시각: ' + stamp, (56, 285), 13)
실행 renderer.wrapped(f"고유 행동 수  {summary['event_count']:,}건", pygame.Rect(56, 312, 290, 36), 20)
실행 renderer.wrapped(f"원본 전달 행 수  {data['raw_record_count']:,}행", pygame.Rect(354, 316, 276, 32), 15)
설정 by_type ← {row['event_type']: row for row in summary['by_action']}
반복 (index, event_type) ← enumerate(ACTION_TYPES):
  설정 left ← 56 + index * 194
  설정 rect ← pygame.Rect(left, 353, 184, 73)
  실행 renderer.card(rect, (235, 241, 229))
  설정 row ← by_type.get(event_type)
  설정 label ← row['action_label'] if row else '해당 행동 항목 없음'
  실행 renderer.wrapped(label, pygame.Rect(left + 10, 360, 164, 23), 15)
  실행 renderer.wrapped(f"{row['count']:,}건" if row else '—', pygame.Rect(left + 10, 389, 164, 28), 20)
실행 renderer.text('방별 행동 수', (56, 437), 15)
설정 rows ← summary['by_room']
조건 not rows 이면:
  실행 renderer.text('표시할 방 항목 없음', (56, 463), 13)
반복 (index, row) ← enumerate(rows[self.page * 4:(self.page + 1) * 4]):
  설정 y ← 461 + index * 23
  실행 renderer.wrapped(row['room_id'], pygame.Rect(56, y, 420, 23), 13)
  실행 renderer.wrapped(f"{row['count']:,}건", pygame.Rect(500, y, 130, 23), 13)
실행 renderer.text('접속자 수·잔액이 아니며, 현재 화면의 이동 횟수와 다를 수 있습니다.', (56, 561), 13)
설정 pages ← max(1, (len(rows) + 3) // 4)
실행 renderer.text(f'방 목록 {self.page + 1}/{pages}', (56, 592), 13)
실행 renderer.button('actions_previous', '이전', self.page > 0)
실행 renderer.button('actions_next', '다음', self.page + 1 < pages)
```

직접 호출 (내부 구현을 펼치지 않음):

```text
(self.response or {}).get
by_type.get
data.get
datetime.fromisoformat
datetime.fromisoformat(summary['generated_at']).astimezone
datetime.fromisoformat(summary['generated_at']).astimezone().isoformat
enumerate
len
max
pygame.Rect
renderer.button
renderer.card
renderer.text
renderer.wrapped
```
