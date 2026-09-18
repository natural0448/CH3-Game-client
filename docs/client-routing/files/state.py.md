# state.py

## 계층과 책임

확정 게임 상태 — 서버 state/snapshot과 command_id/epoch/version을 관리한다. 통계 수치를 좌표·coins로 사용하지 않는다.

원문: `Game-client/state.py`. 호출 경계는 아래 직접 의존성까지만 기술합니다.

## 직접 의존성

```text
from dataclasses import dataclass, field
import time
import uuid
```

## 변수·상수와 출처

인스턴스/지역 변수는 각 함수 의사코드의 설정식이 출처입니다. 필드 갱신은 해당 메서드 항목에만 기록합니다.

```text
설정 (WIDTH, HEIGHT, TILE) ← (20, 15, 32)
설정 GATHER_TILE ← (2, 2)
설정 TRAIN_TILE ← (3, 2)
설정 STATE_FIELDS ← ('player_id', 'room_id', 'x', 'y', 'coins', 'version')
설정 ERROR_MESSAGES ← {'outside_map': '마을 경계 밖으로 이동할 수 없어요.', 'not_at_gather_tile': '채집 장소 (2, 2)로 이동해 주세요.', 'not_at_train_tile': '개인 수련 장소 (3, 2)로 이동해 주세요.', 'too_fast': '조금만 기다린 뒤 다시 행동해 주세요.', 'invalid_direction': '이동 방향을 확인해 주세요.', 'unknown_action': '지원하지 않는 행동이에요.', 'object_required': '명령 형식을 확인해 주세요.'}
클래스 VillageState / 기반 없음
  설정 phase ← 'signed_out'
  설정 message ← '아이디와 비밀번호를 입력해 마을에 입장하세요.'
  설정 own ← None
  설정 players ← field(default_factory=dict)
  설정 pending ← None
  설정 pending_action ← None
  설정 abandoned ← None
  설정 last_sent ← float('-inf')
  설정 epoch ← 0
  설정 online_count ← None
  설정 snapshot_epoch ← None
  설정 ws_messages ← field(default_factory=list)
  설정 has_ws_state ← False
  설정 delivery ← None
  설정 delivery_busy ← False
  설정 delivery_sent_at ← float('-inf')
  설정 show_delivery_api ← False
```

## read_state(data)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `data`: 호출자가 전달한 JSON 객체; 이 함수가 허용 필드를 검증.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
조건 not isinstance(data, dict) or data.get('type') != 'state' 이면:
  실패 전달 ValueError('invalid_state')
설정 result ← {key: data.get(key) for key in STATE_FIELDS}
반복 key ← ('player_id', 'x', 'y', 'coins', 'version'):
  조건 type(result[key]) is not int 이면:
    실패 전달 ValueError('invalid_state')
조건 result['player_id'] <= 0 or not 0 <= result['x'] < WIDTH or (not 0 <= result['y'] < HEIGHT) or (result['coins'] < 0) or (result['version'] < 0) or (not isinstance(result['room_id'], str)) or (not 1 <= len(result['room_id']) <= 32) 이면:
  실패 전달 ValueError('invalid_state')
설정 username ← data.get('username', '')
설정 result['username'] ← username if isinstance(username, str) and len(username) <= 150 else ''
반환 result
```

직접 호출 (내부 구현을 펼치지 않음):

```text
ValueError
data.get
isinstance
len
type
```

## read_snapshot(data)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `data`: 호출자가 전달한 JSON 객체; 이 함수가 허용 필드를 검증.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 players ← data.get('players')
조건 not isinstance(players, list) or len(players) > 20 이면:
  실패 전달 ValueError('invalid_snapshot')
반환 {player['player_id']: player for player in map(read_state, players)}
```

직접 호출 (내부 구현을 펼치지 않음):

```text
ValueError
data.get
isinstance
len
map
```

## VillageState.can_query_delivery(self, *, now=None)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.
- `now`: 테스트 주입 시각; None이면 time.monotonic().

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 now ← time.monotonic() if now is None else now
반환 self.own is not None and self.phase not in ('logging_out', 'signed_out', 'stopped') and (not self.delivery_busy) and (now - self.delivery_sent_at >= 5)
```

직접 호출 (내부 구현을 펼치지 않음):

```text
time.monotonic
```

## VillageState.request_delivery(self, *, now=None)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.
- `now`: 테스트 주입 시각; None이면 time.monotonic().

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 now ← time.monotonic() if now is None else now
조건 not self.can_query_delivery(now=now) 이면:
  반환 None
설정 self.delivery_busy ← True
설정 self.delivery_sent_at ← now
반환 {'kind': 'delivery'}
```

직접 호출 (내부 구현을 펼치지 않음):

```text
self.can_query_delivery
time.monotonic
```

## VillageState.ready(self)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
반환 self.phase == 'connected' and self.own is not None
```

직접 호출 (내부 구현을 펼치지 않음):

```text
없음
```

## VillageState.online_label(self)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
조건 self.online_count is None 이면:
  반환 '온라인 확인 중' if self.own else '온라인 —'
설정 stale ← not self.ready or self.snapshot_epoch != self.epoch
반환 f'온라인 {self.online_count}명' + (' · 마지막 정보' if stale else '')
```

직접 호출 (내부 구현을 펼치지 않음):

```text
없음
```

## VillageState.remember_ws(self, message)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.
- `message`: 호출자가 전달하는 `message`; 값의 사용과 직접 호출 출처는 아래 의사코드에 표시.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
실행 self.ws_messages.append(message)
제거 self.ws_messages[:-3]
```

직접 호출 (내부 구현을 펼치지 않음):

```text
self.ws_messages.append
```

## VillageState.command(self, action, direction=None, *, now=None)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.
- `action`: 호출자가 전달하는 `action`; 값의 사용과 직접 호출 출처는 아래 의사코드에 표시.
- `direction`: 호출자가 전달하는 `direction`; 값의 사용과 직접 호출 출처는 아래 의사코드에 표시.
- `now`: 테스트 주입 시각; None이면 time.monotonic().

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 now ← time.monotonic() if now is None else now
조건 not self.ready or self.pending is not None or now - self.last_sent < 0.2 이면:
  반환 None
조건 action not in ('move', 'gather', 'train') 이면:
  반환 None
조건 action == 'train' and (not self.has_ws_state or (self.own['x'], self.own['y']) != TRAIN_TILE) 이면:
  반환 None
조건 action == 'move' and direction not in ('up', 'down', 'left', 'right') 이면:
  반환 None
설정 command ← {'type': action, 'command_id': str(uuid.uuid4())}
조건 action == 'move' 이면:
  설정 command['direction'] ← direction
설정 self.pending ← command['command_id']
설정 self.pending_action ← action
설정 self.last_sent ← now
설정 self.message ← '서버가 행동을 확인하고 있어요.'
반환 {'kind': 'command', 'epoch': self.epoch, 'command': command}
```

직접 호출 (내부 구현을 펼치지 않음):

```text
str
time.monotonic
uuid.uuid4
```

## VillageState.clear_account(self)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 self.own ← None
실행 self.players.clear()
설정 self.pending, self.abandoned ← None
설정 self.pending_action ← None
설정 self.online_count, self.snapshot_epoch ← None
실행 self.ws_messages.clear()
설정 self.has_ws_state ← False
설정 self.last_sent ← float('-inf')
설정 self.delivery ← None
설정 self.delivery_busy, self.show_delivery_api ← False
설정 self.delivery_sent_at ← float('-inf')
```

직접 호출 (내부 구현을 펼치지 않음):

```text
float
self.players.clear
self.ws_messages.clear
```

## VillageState.accept(self, event)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.
- `event`: network 결과 큐에서 app이 전달한 dict.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 kind ← event.get('kind')
조건 kind == 'status' 이면:
  설정 self.phase ← event['phase']
  설정 self.epoch ← event.get('epoch', self.epoch)
  설정 self.message ← event['message']
  조건 self.phase != 'connected' 이면:
    설정 self.players ← {self.own['player_id']: self.own.copy()} if self.own else {}
  조건 self.phase != 'connected' and self.pending 이면:
    설정 (self.abandoned, self.pending) ← (self.pending, None)
    설정 self.pending_action ← None
    갱신 self.message += ' 전송 중 행동은 재전송하지 않아요.'
그 외:
  조건 kind == 'identity' 이면:
    설정 self.own ← read_state(event['data'])
    설정 self.players ← {self.own['player_id']: self.own.copy()}
  그 외:
    조건 kind == 'snapshot' 이면:
      조건 event.get('epoch') != self.epoch or self.own is None 이면:
        반환 None
      설정 members ← read_snapshot(event['data'])
      설정 display ← {}
      반복 (player_id, incoming) ← members.items():
        조건 incoming['room_id'] != self.own['room_id'] 이면:
          다음 반복으로
        조건 player_id == self.own['player_id'] 이면:
          설정 display[player_id] ← self.own.copy()
        그 외:
          설정 previous ← self.players.get(player_id)
          설정 display[player_id] ← (previous if previous and previous['version'] > incoming['version'] else incoming).copy()
      설정 self.players ← display
      설정 self.online_count ← len(display)
      설정 self.snapshot_epoch ← self.epoch
      실행 self.remember_ws(f"snapshot · {self.own['room_id']} · {self.online_count}명")
    그 외:
      조건 kind == 'state' 이면:
        조건 event.get('epoch') != self.epoch 이면:
          반환 None
        설정 data ← event['data']
        설정 incoming ← read_state(data)
        조건 self.own is None or incoming['room_id'] != self.own['room_id'] 이면:
          반환 None
        실행 self.remember_ws(f"state · #{incoming['player_id']} · ({incoming['x']}, {incoming['y']}) · 동전 {incoming['coins']} · v{incoming['version']}")
        조건 incoming['player_id'] != self.own['player_id'] 이면:
          설정 previous ← self.players.get(incoming['player_id'])
          조건 previous is None or incoming['version'] >= previous['version'] 이면:
            설정 self.players[incoming['player_id']] ← incoming.copy()
          반환 None
        조건 incoming['version'] < self.own['version'] 이면:
          반환 None
        조건 self.pending_action == 'train' and self.pending and (data.get('command_id') != self.pending) 이면:
          반환 None
        설정 self.own ← incoming
        설정 self.has_ws_state ← True
        설정 self.players[incoming['player_id']] ← incoming.copy()
        설정 self.phase ← 'connected'
        조건 self.pending and data.get('command_id') == self.pending 이면:
          설정 self.pending ← None
          설정 trained ← self.pending_action == 'train'
          설정 self.pending_action ← None
          설정 self.message ← '수련 완료 · 동전 1 획득' if trained else '서버가 상태를 확정했어요.'
        그 외:
          조건 event.get('first') 이면:
            설정 self.message ← '서버 상태를 받았어요. 방향키 또는 버튼으로 이동하세요.'
      그 외:
        조건 kind == 'error' and event.get('epoch') == self.epoch 이면:
          조건 self.pending and event.get('command_id') == self.pending 이면:
            설정 self.pending ← None
            설정 self.pending_action ← None
          설정 code ← event.get('code')
          설정 self.message ← ERROR_MESSAGES.get(code, '서버가 행동을 거절했어요.')
          실행 self.remember_ws('error · ' + self.message)
        그 외:
          조건 kind == 'delivery' 이면:
            조건 self.own is None or event.get('player_id') != self.own['player_id'] or self.phase == 'logging_out' 이면:
              반환 None
            설정 self.delivery_busy ← False
            설정 self.delivery ← {key: event[key] for key in ('path', 'status', 'json', 'message')}
          그 외:
            조건 kind == 'notice' 이면:
              설정 self.message ← event['message']
            그 외:
              조건 kind in ('logged_out', 'login_failed') 이면:
                실행 self.clear_account()
                설정 self.phase ← 'signed_out'
                설정 self.message ← event['message']
              그 외:
                조건 kind == 'stopped' 이면:
                  실행 self.clear_account()
                  설정 self.phase ← 'stopped'
```

직접 호출 (내부 구현을 펼치지 않음):

```text
(previous if previous and previous['version'] > incoming['version'] else incoming).copy
ERROR_MESSAGES.get
data.get
event.get
incoming.copy
len
members.items
read_snapshot
read_state
self.clear_account
self.own.copy
self.players.get
self.remember_ws
```
