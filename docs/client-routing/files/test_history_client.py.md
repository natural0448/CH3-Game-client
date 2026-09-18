# test_history_client.py

## 계층과 책임

회귀 검증 — 해당 기능의 오프라인 입력·기대 결과·fake session을 검증한다.

원문: `Game-client/test_history_client.py`. 호출 경계는 아래 직접 의존성까지만 기술합니다.

## 직접 의존성

```text
from history_data import read_history
from network import NetworkWorker
from panels import HistoryPanel
from state import VillageState
from test_delivery_client import Response, Session
from test_multiplayer import player
from uuid import uuid4
import asyncio
import copy
import unittest
```

## 변수·상수와 출처

인스턴스/지역 변수는 각 함수 의사코드의 설정식이 출처입니다. 필드 갱신은 해당 메서드 항목에만 기록합니다.

```text
클래스 TrainStateTests / 기반 unittest.TestCase
클래스 HistoryNetworkTests / 기반 unittest.IsolatedAsyncioTestCase
```

## history_data()

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- 없음.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
반환 {'scope': 'current-player', 'limit': 20, 'events': [{'schema_version': 1, 'event_id': str(uuid4()), 'event_type': 'player.trained', 'player_id': 1, 'room_id': 'room-01', 'event_time': '2026-09-16T07:00:00+00:00', 'payload': {'x': 3, 'y': 2, 'coins': 1, 'version': 6, 'transition': {'episode_id': str(uuid4()), 'step': 1, 'reward': 1, 'observation': {'x': 3, 'y': 2, 'coins': 0}, 'next_observation': {'x': 3, 'y': 2, 'coins': 1}, 'action': {'type': 'train'}, 'done': False, 'terminated': False, 'truncated': False, 'policy_version': 'manual-v1'}}}]}
```

직접 호출 (내부 구현을 펼치지 않음):

```text
str
uuid4
```

## TrainStateTests.setUp(self)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 self.state ← VillageState()
실행 self.state.accept({'kind': 'identity', 'data': player(x=3, y=2)})
실행 self.state.accept({'kind': 'status', 'phase': 'connecting', 'epoch': 1, 'message': 'wait'})
실행 self.state.accept({'kind': 'state', 'data': player(x=3, y=2), 'epoch': 1, 'first': True})
```

직접 호출 (내부 구현을 펼치지 않음):

```text
VillageState
player
self.state.accept
```

## TrainStateTests.test_train_payload_and_matching_ack_keeps_history_closed(self)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 state ← self.state
설정 panel ← HistoryPanel()
설정 request ← state.command('train', now=1)
설정 command_id ← request['command']['command_id']
실행 self.assertEqual(set(request['command']), {'type', 'command_id'})
실행 self.assertEqual(request['command']['type'], 'train')
실행 self.assertIsNone(state.command('train', now=2))
실행 self.assertEqual(state.own['coins'], 0)
실행 state.accept({'kind': 'state', 'epoch': 1, 'data': player(2, command_id=command_id, coins=1, version=1)})
실행 self.assertEqual(state.pending, command_id)
실행 self.assertFalse(panel.opened)
실행 state.accept({'kind': 'state', 'epoch': 1, 'data': player(x=3, y=2, command_id='unrelated', coins=1, version=1)})
실행 self.assertEqual(state.own['coins'], 0)
실행 self.assertEqual(state.pending, command_id)
실행 state.accept({'kind': 'state', 'epoch': 1, 'data': player(x=3, y=2, command_id=command_id, coins=1, version=1)})
실행 self.assertIsNone(state.pending)
실행 self.assertEqual(state.own['coins'], 1)
실행 panel.accept({'kind': 'state', 'epoch': 1, 'data': state.own}, state)
실행 self.assertFalse(panel.opened)
실행 self.assertFalse(panel.busy)
실행 self.assertIn('수련 완료', state.message)
실행 self.assertIsNone(state.command('train', now=1.1))
실행 state.clear_account()
실행 self.assertIsNone(state.pending_action)
```

직접 호출 (내부 구현을 펼치지 않음):

```text
HistoryPanel
panel.accept
player
self.assertEqual
self.assertFalse
self.assertIn
self.assertIsNone
set
state.accept
state.clear_account
state.command
```

## TrainStateTests.test_tile_first_state_disconnect_and_error_gates(self)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 state ← self.state
설정 state.has_ws_state ← False
실행 self.assertIsNone(state.command('train', now=1))
설정 state.has_ws_state ← True
설정 state.own['x'] ← 2
실행 self.assertIsNone(state.command('train', now=1))
설정 state.own['x'] ← 3
설정 request ← state.command('train', now=1)
실행 state.accept({'kind': 'error', 'epoch': 1, 'command_id': request['command']['command_id'], 'code': 'not_at_train_tile'})
실행 self.assertIsNone(state.pending_action)
실행 self.assertEqual(state.own['coins'], 0)
실행 state.accept({'kind': 'status', 'phase': 'disconnected', 'epoch': 1, 'message': 'lost'})
실행 self.assertIsNone(state.command('train', now=2))
```

직접 호출 (내부 구현을 펼치지 않음):

```text
self.assertEqual
self.assertIsNone
state.accept
state.command
```

## TrainStateTests.test_history_panel_ignores_other_or_stale_requests_and_clears_on_logout(self)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 panel ← HistoryPanel()
설정 request ← panel.request(self.state)
실행 self.assertEqual(request['kind'], 'history')
설정 event ← dict(kind='history', request_id=request['request_id'], player_id=2)
실행 panel.accept(event, self.state)
실행 self.assertTrue(panel.busy)
실행 event.update(player_id=1, path='GET /api/history/', status=200, json=history_data(), message='done')
설정 original ← copy.deepcopy(self.state.own)
실행 panel.accept(event, self.state)
실행 self.assertFalse(panel.busy)
실행 self.assertEqual(self.state.own, original)
실행 panel.accept({'kind': 'logged_out'}, self.state)
실행 self.assertIsNone(panel.response)
```

직접 호출 (내부 구현을 펼치지 않음):

```text
HistoryPanel
copy.deepcopy
dict
event.update
history_data
panel.accept
panel.request
self.assertEqual
self.assertFalse
self.assertIsNone
self.assertTrue
```

## HistoryNetworkTests.worker(self, response)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.
- `response`: worker가 허용 목록으로 만든 path/status/json/message dict.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 worker ← NetworkWorker({'server_base_url': 'http://127.0.0.1:8000'})
설정 worker.identity ← 1
설정 worker.session ← Session(response)
반환 worker
```

직접 호출 (내부 구현을 펼치지 않음):

```text
NetworkWorker
Session
```

## HistoryNetworkTests.test_same_session_sanitized_queue_and_missing_transition(self)

비동기 함수: worker loop 또는 테스트 loop에서 await한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 data ← history_data()
설정 data['password'] ← 'exclude-me'
설정 data['events'][0]['payload']['transition']['action']['token'] ← 'exclude-me'
설정 worker ← self.worker(Response(data=data))
설정 worker.pending ← 'game-command'
실행 await worker._history({'player_id': 1, 'request_id': 'read-1'})
설정 event ← worker.events.get_nowait()
실행 self.assertEqual(event['status'], 200)
실행 self.assertEqual(event['request_id'], 'read-1')
실행 self.assertNotIn('exclude-me', str(event))
설정 (args, kwargs) ← worker.session.calls[0]
실행 self.assertEqual(args, ('GET', 'http://127.0.0.1:8000/api/history/'))
실행 self.assertFalse(kwargs['allow_redirects'])
실행 self.assertEqual(kwargs['timeout'].total, 8)
실행 self.assertEqual(worker.pending, 'game-command')
제거 data['events'][0]['payload']['transition']
실행 self.assertNotIn('transition', read_history(data, 1)['events'][0]['payload'])
자원 범위 self.assertRaises(ValueError):
  실행 read_history(data, 2)
```

직접 호출 (내부 구현을 펼치지 않음):

```text
Response
history_data
read_history
self.assertEqual
self.assertFalse
self.assertNotIn
self.assertRaises
self.worker
str
worker._history
worker.events.get_nowait
```

## HistoryNetworkTests.test_html_and_login_responses_are_not_parsed(self)

비동기 함수: worker loop 또는 테스트 loop에서 await한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
반복 status ← (200, 302, 401):
  설정 response ← Response(status=status, content_type='text/html', raw=b'private')
  설정 worker ← self.worker(response)
  실행 await worker._history({'player_id': 1})
  설정 event ← worker.events.get_nowait()
  실행 self.assertIsNone(event['json'])
  실행 self.assertFalse(response.body_read)
  조건 status != 200 이면:
    실행 self.assertIn('로그인', event['message'])
```

직접 호출 (내부 구현을 펼치지 않음):

```text
Response
self.assertFalse
self.assertIn
self.assertIsNone
self.worker
worker._history
worker.events.get_nowait
```

## HistoryNetworkTests.test_slow_history_does_not_block_commands_and_cleanup_cancels_it(self)

비동기 함수: worker loop 또는 테스트 loop에서 await한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 worker ← self.worker(Response(data={}))
설정 (started, moved, cancelled) ← (asyncio.Event(), asyncio.Event(), asyncio.Event())
내부 함수 slow_history 정의 → 아래 별도 시그니처 문서 참조
내부 함수 command 정의 → 아래 별도 시그니처 문서 참조
내부 함수 close 정의 → 아래 별도 시그니처 문서 참조
설정 (worker._history, worker._command) ← (slow_history, command)
설정 worker.session.close ← close
설정 worker.session.cookie_jar ← type('Jar', (), {'clear': lambda self: None})()
설정 task ← asyncio.create_task(worker._run())
시도:
  실행 worker.submit({'kind': 'history'})
  실행 await asyncio.wait_for(started.wait(), 1)
  실행 worker.submit({'kind': 'command'})
  실행 await asyncio.wait_for(moved.wait(), 1)
항상 정리:
  실행 task.cancel()
  실행 await asyncio.gather(task, return_exceptions=True)
실행 self.assertTrue(cancelled.is_set())
```

직접 호출 (내부 구현을 펼치지 않음):

```text
Response
asyncio.Event
asyncio.create_task
asyncio.gather
asyncio.wait_for
cancelled.is_set
moved.wait
self.assertTrue
self.worker
started.wait
task.cancel
type
type('Jar', (), {'clear': lambda self: None})
worker._run
worker.submit
```

## HistoryNetworkTests.test_slow_history_does_not_block_commands_and_cleanup_cancels_it.slow_history(request)

비동기 함수: worker loop 또는 테스트 loop에서 await한다.

파라미터:
- `request`: app이 요청 큐에 넣은 dict; kind/request_id/player_id 또는 명령.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
실행 started.set()
시도:
  실행 await asyncio.Event().wait()
항상 정리:
  실행 cancelled.set()
```

직접 호출 (내부 구현을 펼치지 않음):

```text
asyncio.Event
asyncio.Event().wait
cancelled.set
started.set
```

## HistoryNetworkTests.test_slow_history_does_not_block_commands_and_cleanup_cancels_it.command(request)

비동기 함수: worker loop 또는 테스트 loop에서 await한다.

파라미터:
- `request`: app이 요청 큐에 넣은 dict; kind/request_id/player_id 또는 명령.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
실행 moved.set()
```

직접 호출 (내부 구현을 펼치지 않음):

```text
moved.set
```

## HistoryNetworkTests.test_slow_history_does_not_block_commands_and_cleanup_cancels_it.close()

비동기 함수: worker loop 또는 테스트 loop에서 await한다.

파라미터:
- 없음.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
추가 동작 없음
```

직접 호출 (내부 구현을 펼치지 않음):

```text
없음
```
