# test_multiplayer.py

## 계층과 책임

회귀 검증 — 해당 기능의 오프라인 입력·기대 결과·fake session을 검증한다.

원문: `Game-client/test_multiplayer.py`. 호출 경계는 아래 직접 의존성까지만 기술합니다.

## 직접 의존성

```text
from network import NetworkWorker
from state import VillageState
from types import SimpleNamespace
import aiohttp
import asyncio
import json
import unittest
```

## 변수·상수와 출처

인스턴스/지역 변수는 각 함수 의사코드의 설정식이 출처입니다. 필드 갱신은 해당 메서드 항목에만 기록합니다.

```text
클래스 MultiplayerStateTests / 기반 unittest.TestCase
클래스 FakeSocket / 기반 없음
클래스 MultiplayerNetworkTests / 기반 unittest.IsolatedAsyncioTestCase
```

## player(pid=1, **changes)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `pid`: 호출자가 전달하는 `pid`; 값의 사용과 직접 호출 출처는 아래 의사코드에 표시.
- `changes`: 호출자가 전달하는 `changes`; 값의 사용과 직접 호출 출처는 아래 의사코드에 표시.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
반환 {'type': 'state', 'player_id': pid, 'room_id': 'room-01', 'x': 0, 'y': 0, 'coins': 0, 'version': 0, **changes}
```

직접 호출 (내부 구현을 펼치지 않음):

```text
없음
```

## MultiplayerStateTests.setUp(self)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 self.state ← VillageState()
실행 self.state.accept({'kind': 'identity', 'data': player()})
실행 self.state.accept({'kind': 'status', 'phase': 'connecting', 'epoch': 1, 'message': 'wait'})
실행 self.state.accept({'kind': 'state', 'data': player(), 'epoch': 1, 'first': True})
```

직접 호출 (내부 구현을 펼치지 않음):

```text
VillageState
player
self.state.accept
```

## MultiplayerStateTests.snapshot(self, *players, epoch=1)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.
- `epoch`: 호출자가 전달하는 `epoch`; 값의 사용과 직접 호출 출처는 아래 의사코드에 표시.
- `players`: 호출자가 전달하는 `players`; 값의 사용과 직접 호출 출처는 아래 의사코드에 표시.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
실행 self.state.accept({'kind': 'snapshot', 'epoch': epoch, 'data': {'type': 'snapshot', 'players': list(players)}})
```

직접 호출 (내부 구현을 펼치지 않음):

```text
list
self.state.accept
```

## MultiplayerStateTests.test_join_move_and_departure(self)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
실행 self.snapshot(player(), player(2))
실행 self.assertEqual(set(self.state.players), {1, 2})
실행 self.state.accept({'kind': 'state', 'epoch': 1, 'data': player(2, x=4, version=1)})
실행 self.assertEqual(self.state.players[2]['x'], 4)
실행 self.assertEqual(self.state.own['x'], 0)
실행 self.snapshot(player())
실행 self.assertEqual(set(self.state.players), {1})
```

직접 호출 (내부 구현을 펼치지 않음):

```text
player
self.assertEqual
self.snapshot
self.state.accept
set
```

## MultiplayerStateTests.test_snapshot_and_other_players_never_ack_my_command(self)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 request ← self.state.command('move', 'right', now=1)
설정 pending ← request['command']['command_id']
실행 self.snapshot(player(x=9, version=9), player(2, version=99))
실행 self.assertEqual(self.state.own['x'], 0)
실행 self.assertEqual(self.state.players[1]['x'], 0)
실행 self.state.accept({'kind': 'state', 'epoch': 1, 'data': player(2, version=100, command_id=pending)})
실행 self.assertEqual(self.state.pending, pending)
실행 self.state.accept({'kind': 'state', 'epoch': 1, 'data': player(x=1, version=1, command_id=pending)})
실행 self.assertIsNone(self.state.pending)
실행 self.assertEqual(self.state.own['x'], 1)
```

직접 호출 (내부 구현을 펼치지 않음):

```text
player
self.assertEqual
self.assertIsNone
self.snapshot
self.state.accept
self.state.command
```

## MultiplayerStateTests.test_room_epoch_and_version_boundaries(self)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
실행 self.snapshot(player(), player(2, x=5, version=5), player(3, room_id='room-02'))
실행 self.assertEqual(set(self.state.players), {1, 2})
실행 self.snapshot(player(), player(2, x=0, version=1))
실행 self.assertEqual(self.state.players[2]['x'], 5)
실행 self.snapshot(player(), epoch=0)
실행 self.assertIn(2, self.state.players)
실행 self.state.accept({'kind': 'state', 'epoch': 1, 'data': player(3, room_id='room-02')})
실행 self.assertNotIn(3, self.state.players)
실행 self.state.accept({'kind': 'status', 'phase': 'disconnected', 'message': 'lost', 'epoch': 1})
실행 self.assertEqual(set(self.state.players), {1})
실행 self.assertFalse(self.state.ready)
실행 self.state.accept({'kind': 'logged_out', 'message': 'bye'})
실행 self.assertFalse(self.state.players)
```

직접 호출 (내부 구현을 펼치지 않음):

```text
player
self.assertEqual
self.assertFalse
self.assertIn
self.assertNotIn
self.snapshot
self.state.accept
set
```

## MultiplayerStateTests.test_online_snapshot_disconnect_reconnect_and_error_message(self)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
실행 self.assertIsNone(self.state.online_count)
실행 self.snapshot(player(), player(2, username='bob'), player(3, room_id='room-02'))
실행 self.assertEqual(self.state.online_label, '온라인 2명')
실행 self.state.accept({'kind': 'error', 'epoch': 1, 'code': 'not_at_gather_tile'})
설정 error_message ← self.state.message
실행 self.state.accept({'kind': 'state', 'epoch': 1, 'data': player(2, version=1, coins=5, username='bob')})
실행 self.assertEqual(self.state.message, error_message)
실행 self.assertEqual(self.state.own['coins'], 0)
실행 self.assertEqual(self.state.players[2]['username'], 'bob')
실행 self.state.accept({'kind': 'status', 'phase': 'disconnected', 'epoch': 1, 'message': 'lost'})
실행 self.assertEqual(self.state.online_label, '온라인 2명 · 마지막 정보')
실행 self.state.accept({'kind': 'status', 'phase': 'reconnecting', 'epoch': 2, 'message': 'retry'})
실행 self.state.accept({'kind': 'state', 'epoch': 2, 'data': player(), 'first': True})
실행 self.assertIn('마지막 정보', self.state.online_label)
실행 self.snapshot(player(), epoch=1)
실행 self.assertEqual(self.state.online_count, 2)
실행 self.snapshot(player(), epoch=2)
실행 self.assertEqual(self.state.online_label, '온라인 1명')
실행 self.assertLessEqual(len(self.state.ws_messages), 3)
실행 self.state.clear_account()
실행 self.assertIsNone(self.state.online_count)
실행 self.assertEqual(self.state.ws_messages, [])
```

직접 호출 (내부 구현을 펼치지 않음):

```text
len
player
self.assertEqual
self.assertIn
self.assertIsNone
self.assertLessEqual
self.snapshot
self.state.accept
self.state.clear_account
```

## FakeSocket.__init__(self)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 self.incoming ← asyncio.Queue()
설정 self.closed ← False
```

직접 호출 (내부 구현을 펼치지 않음):

```text
asyncio.Queue
```

## FakeSocket.receive(self)

비동기 함수: worker loop 또는 테스트 loop에서 await한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 data ← await self.incoming.get()
반환 SimpleNamespace(type=aiohttp.WSMsgType.TEXT, data=json.dumps(data))
```

직접 호출 (내부 구현을 펼치지 않음):

```text
SimpleNamespace
json.dumps
self.incoming.get
```

## FakeSocket.close(self)

비동기 함수: worker loop 또는 테스트 loop에서 await한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 self.closed ← True
```

직접 호출 (내부 구현을 펼치지 않음):

```text
없음
```

## MultiplayerNetworkTests.test_worker_forwards_room_members_without_mixing_my_ack_or_version(self)

비동기 함수: worker loop 또는 테스트 loop에서 await한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 worker ← NetworkWorker({'server_base_url': 'http://127.0.0.1:8000'})
설정 (worker.identity, worker.room_id, worker.version) ← (1, 'room-01', 0)
설정 socket ← FakeSocket()
내부 함수 connect 정의 → 아래 별도 시그니처 문서 참조
설정 worker.session ← SimpleNamespace(ws_connect=connect)
설정 task ← asyncio.create_task(worker._websockets())
내부 함수 deliver 정의 → 아래 별도 시그니처 문서 참조
시도:
  설정 event ← await deliver(player(2, version=90), 'state')
  실행 self.assertFalse(event['first'])
  실행 self.assertFalse(worker.ready)
  실행 self.assertEqual(worker.version, 0)
  설정 event ← await deliver(player(), 'state')
  실행 self.assertTrue(event['first'])
  실행 self.assertTrue(worker.ready)
  설정 worker.pending ← 'my-command'
  설정 event ← await deliver({'type': 'snapshot', 'players': [player(), player(2), player(3, room_id='room-02')]}, 'snapshot')
  실행 self.assertEqual([p['player_id'] for p in event['data']['players']], [1, 2])
  실행 self.assertEqual(worker.pending, 'my-command')
  실행 await deliver(player(2, version=99, command_id='my-command'), 'state')
  실행 self.assertEqual(worker.pending, 'my-command')
  실행 self.assertEqual(worker.version, 0)
  실행 await deliver(player(version=1, command_id='my-command'), 'state')
  실행 self.assertIsNone(worker.pending)
  실행 self.assertEqual(worker.version, 1)
항상 정리:
  실행 task.cancel()
  실행 await asyncio.gather(task, return_exceptions=True)
  실행 self.assertTrue(socket.closed)
```

직접 호출 (내부 구현을 펼치지 않음):

```text
FakeSocket
NetworkWorker
SimpleNamespace
asyncio.create_task
asyncio.gather
deliver
player
self.assertEqual
self.assertFalse
self.assertIsNone
self.assertTrue
task.cancel
worker._websockets
```

## MultiplayerNetworkTests.test_worker_forwards_room_members_without_mixing_my_ack_or_version.connect(url, **kwargs)

비동기 함수: worker loop 또는 테스트 loop에서 await한다.

파라미터:
- `url`: 호출자가 전달하는 `url`; 값의 사용과 직접 호출 출처는 아래 의사코드에 표시.
- `kwargs`: 호출자가 전달하는 `kwargs`; 값의 사용과 직접 호출 출처는 아래 의사코드에 표시.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
실행 self.assertEqual(kwargs['origin'], 'http://127.0.0.1:8000')
반환 socket
```

직접 호출 (내부 구현을 펼치지 않음):

```text
self.assertEqual
```

## MultiplayerNetworkTests.test_worker_forwards_room_members_without_mixing_my_ack_or_version.deliver(data, kind)

비동기 함수: worker loop 또는 테스트 loop에서 await한다.

파라미터:
- `data`: 호출자가 전달한 JSON 객체; 이 함수가 허용 필드를 검증.
- `kind`: app/network가 사용하는 고정 요청·결과 종류.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
실행 await socket.incoming.put(data)
비동기 자원 범위 asyncio.timeout(2):
  반복 True:
    반복 not worker.events.empty():
      설정 event ← worker.events.get_nowait()
      조건 event['kind'] == kind 이면:
        반환 event
    실행 await asyncio.sleep(0.001)
```

직접 호출 (내부 구현을 펼치지 않음):

```text
asyncio.sleep
asyncio.timeout
socket.incoming.put
worker.events.empty
worker.events.get_nowait
```
