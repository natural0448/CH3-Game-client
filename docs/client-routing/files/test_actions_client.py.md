# test_actions_client.py

## 계층과 책임

회귀 검증 — 해당 기능의 오프라인 입력·기대 결과·fake session을 검증한다.

원문: `Game-client/test_actions_client.py`. 호출 경계는 아래 직접 의존성까지만 기술합니다.

## 직접 의존성

```text
from actions_panel import ActionsPanel
from analytics_data import read_actions
from network import NetworkWorker
from render import Renderer
from state import VillageState
from test_delivery_client import Response, Session
from test_multiplayer import player
import asyncio
import copy
import os
import pygame
import unittest
```

## 변수·상수와 출처

인스턴스/지역 변수는 각 함수 의사코드의 설정식이 출처입니다. 필드 갱신은 해당 메서드 항목에만 기록합니다.

```text
클래스 ActionContractTests / 기반 unittest.TestCase
클래스 ActionNetworkTests / 기반 unittest.IsolatedAsyncioTestCase
클래스 ActionRenderingTests / 기반 unittest.TestCase
```

## snapshot()

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- 없음.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
반환 {'available': True, 'source_topic': 'game.actions.v1', 'source_kind': 'bounded-kafka-snapshot', 'raw_record_count': 12, 'label_source': 'current-display-map', 'bounds': [{'partition': 0, 'start_inclusive': 0, 'end_exclusive': 12}], 'summary': {'generated_at': '2026-09-17T07:24:52+00:00', 'event_count': 10, 'by_action': [{'event_type': 'player.moved', 'action_label': '이동', 'count': 7}, {'event_type': 'player.gathered', 'action_label': '개인 채집', 'count': 2}, {'event_type': 'player.trained', 'action_label': '개인 수련', 'count': 1}], 'by_room': [{'room_id': 'room-01', 'count': 10}]}}
```

직접 호출 (내부 구현을 펼치지 않음):

```text
없음
```

## ActionContractTests.test_allowlist_and_original_data_unchanged(self)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 data ← snapshot()
설정 data['csrfToken'] ← 'private'
설정 data['summary']['cookie'] ← 'private'
설정 data['summary']['by_action'][0]['password'] ← 'private'
설정 data['bounds'][0]['session'] ← 'private'
설정 before ← copy.deepcopy(data)
설정 clean ← read_actions(data)
실행 self.assertNotIn('private', str(clean))
실행 self.assertEqual(data, before)
실행 self.assertEqual(clean['summary']['event_count'], 10)
실행 self.assertEqual(clean['raw_record_count'], 12)
```

직접 호출 (내부 구현을 펼치지 않음):

```text
copy.deepcopy
read_actions
self.assertEqual
self.assertNotIn
snapshot
str
```

## ActionContractTests.test_unavailable_is_not_zero_and_zero_is_a_real_result(self)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
실행 self.assertEqual(read_actions({'available': False, 'event_count': 0}), {'available': False, 'summary': None})
설정 data ← snapshot()
설정 data['raw_record_count'], data['summary']['event_count'] ← 0
설정 data['summary']['by_action'] ← []
설정 data['summary']['by_room'] ← []
실행 self.assertEqual(read_actions(data)['summary']['event_count'], 0)
```

직접 호출 (내부 구현을 펼치지 않음):

```text
read_actions
self.assertEqual
snapshot
```

## ActionContractTests.test_malformed_metrics_are_rejected(self)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 bad ← []
반복 (key, value) ← (('raw_record_count', True), ('source_kind', 'live'), ('available', 1)):
  설정 data ← snapshot()
  설정 data[key] ← value
  실행 bad.append(data)
반복 (key, value) ← (('generated_at', '2026-09-17'), ('event_count', -1), ('by_room', None)):
  설정 data ← snapshot()
  설정 data['summary'][key] ← value
  실행 bad.append(data)
설정 data ← snapshot()
설정 data['summary']['by_action'][1] ← data['summary']['by_action'][0]
실행 bad.append(data)
반복 data ← bad:
  자원 범위 self.subTest(data=data), self.assertRaises(ValueError):
    실행 read_actions(data)
```

직접 호출 (내부 구현을 펼치지 않음):

```text
bad.append
read_actions
self.assertRaises
self.subTest
snapshot
```

## ActionContractTests.test_panel_correlates_requests_and_never_mutates_game_state(self)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 state ← VillageState(phase='connected', own=player(), pending='move-id')
설정 before ← copy.deepcopy(state)
설정 panel ← ActionsPanel()
설정 request ← panel.request(state)
실행 self.assertIsNone(panel.request(state))
설정 event ← dict(kind='actions', request_id='old', player_id=1, path='GET /api/analytics/actions/', status=200, json=read_actions(snapshot()), message='done')
실행 panel.accept(event, state)
실행 self.assertTrue(panel.busy)
설정 event['request_id'] ← request['request_id']
설정 event['player_id'] ← 2
실행 panel.accept(event, state)
실행 self.assertTrue(panel.busy)
설정 event['player_id'] ← 1
실행 state.accept(event)
실행 panel.accept(event, state)
실행 self.assertFalse(panel.busy)
실행 self.assertEqual(state, before)
실행 panel.accept({'kind': 'logged_out'}, state)
실행 panel.accept(event, state)
실행 self.assertIsNone(panel.response)
```

직접 호출 (내부 구현을 펼치지 않음):

```text
ActionsPanel
VillageState
copy.deepcopy
dict
panel.accept
panel.request
player
read_actions
self.assertEqual
self.assertFalse
self.assertIsNone
self.assertTrue
snapshot
state.accept
```

## ActionNetworkTests.worker(self, response)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.
- `response`: worker가 허용 목록으로 만든 path/status/json/message dict.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 worker ← NetworkWorker({'server_base_url': 'http://127.0.0.1:8000'})
설정 worker.session ← Session(response)
설정 worker.identity ← 1
설정 worker.pending ← 'move-id'
반환 worker
```

직접 호출 (내부 구현을 펼치지 않음):

```text
NetworkWorker
Session
```

## ActionNetworkTests.test_get_same_session_and_safe_queue(self)

비동기 함수: worker loop 또는 테스트 loop에서 await한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 worker ← self.worker(Response(data=snapshot()))
설정 session ← worker.session
실행 await worker._actions({'request_id': 'query-id', 'player_id': 1})
설정 result ← worker.events.get_nowait()
실행 self.assertEqual(result['kind'], 'actions')
실행 self.assertEqual(result['request_id'], 'query-id')
실행 self.assertEqual(result['json']['summary']['event_count'], 10)
실행 self.assertEqual(worker.pending, 'move-id')
실행 self.assertIs(worker.session, session)
설정 (args, kwargs) ← session.calls[0]
실행 self.assertEqual(args, ('GET', 'http://127.0.0.1:8000/api/analytics/actions/'))
실행 self.assertFalse(kwargs['allow_redirects'])
실행 self.assertEqual(kwargs['timeout'].total, 8)
```

직접 호출 (내부 구현을 펼치지 않음):

```text
Response
self.assertEqual
self.assertFalse
self.assertIs
self.worker
snapshot
worker._actions
worker.events.get_nowait
```

## ActionNetworkTests.test_redirect_html_timeout_and_missing_are_not_zero(self)

비동기 함수: worker loop 또는 테스트 loop에서 await한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
반복 status ← (302, 401, 404, 500, 200):
  설정 response ← Response(status=status, content_type='text/html', raw=b'private cookie')
  설정 worker ← self.worker(response)
  실행 await worker._actions({'player_id': 1})
  설정 result ← worker.events.get_nowait()
  실행 self.assertFalse(response.body_read)
  실행 self.assertIsNone(result['json'])
  실행 self.assertNotIn('private', str(result))
  조건 status in (302, 401) 이면:
    실행 self.assertIn('로그인', result['message'])
설정 worker ← self.worker(Response(data={'available': False}))
실행 await worker._actions({'player_id': 1})
실행 self.assertEqual(worker.events.get_nowait()['message'], '행동 집계가 아직 없습니다')
내부 함수 timeout 정의 → 아래 별도 시그니처 문서 참조
설정 worker._json ← timeout
실행 await worker._actions({'player_id': 1})
실행 self.assertIsNone(worker.events.get_nowait()['json'])
```

직접 호출 (내부 구현을 펼치지 않음):

```text
Response
self.assertEqual
self.assertFalse
self.assertIn
self.assertIsNone
self.assertNotIn
self.worker
str
worker._actions
worker.events.get_nowait
```

## ActionNetworkTests.test_redirect_html_timeout_and_missing_are_not_zero.timeout(*args)

비동기 함수: worker loop 또는 테스트 loop에서 await한다.

파라미터:
- `args`: 호출자가 전달하는 `args`; 값의 사용과 직접 호출 출처는 아래 의사코드에 표시.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
실패 전달 asyncio.TimeoutError()
```

직접 호출 (내부 구현을 펼치지 않음):

```text
asyncio.TimeoutError
```

## ActionNetworkTests.test_slow_query_keeps_command_queue_live_and_cancels_on_close(self)

비동기 함수: worker loop 또는 테스트 loop에서 await한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 worker ← self.worker(Response(data=snapshot()))
설정 worker.pending ← None
설정 (started, moved, cancelled) ← (asyncio.Event(), asyncio.Event(), asyncio.Event())
내부 함수 slow_json 정의 → 아래 별도 시그니처 문서 참조
내부 함수 command 정의 → 아래 별도 시그니처 문서 참조
내부 함수 close 정의 → 아래 별도 시그니처 문서 참조
설정 (worker._json, worker._command) ← (slow_json, command)
설정 worker.session.close ← close
설정 worker.session.cookie_jar ← type('Jar', (), {'clear': lambda self: None})()
설정 task ← asyncio.create_task(worker._run())
시도:
  실행 await asyncio.sleep(0.02)
  실행 self.assertFalse(started.is_set())
  실행 worker.submit({'kind': 'actions', 'request_id': 'query-id', 'player_id': 1})
  실행 await asyncio.wait_for(started.wait(), 1)
  실행 worker.submit({'kind': 'command'})
  실행 await asyncio.wait_for(moved.wait(), 1)
항상 정리:
  실행 task.cancel()
  실행 await asyncio.gather(task, return_exceptions=True)
실행 self.assertTrue(cancelled.is_set())
실행 self.assertIsNone(worker.actions_task)
실행 self.assertIsNone(worker.session)
```

직접 호출 (내부 구현을 펼치지 않음):

```text
Response
asyncio.Event
asyncio.create_task
asyncio.gather
asyncio.sleep
asyncio.wait_for
cancelled.is_set
moved.wait
self.assertFalse
self.assertIsNone
self.assertTrue
self.worker
snapshot
started.is_set
started.wait
task.cancel
type
type('Jar', (), {'clear': lambda self: None})
worker._run
worker.submit
```

## ActionNetworkTests.test_slow_query_keeps_command_queue_live_and_cancels_on_close.slow_json(*args)

비동기 함수: worker loop 또는 테스트 loop에서 await한다.

파라미터:
- `args`: 호출자가 전달하는 `args`; 값의 사용과 직접 호출 출처는 아래 의사코드에 표시.

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

## ActionNetworkTests.test_slow_query_keeps_command_queue_live_and_cancels_on_close.command(request)

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

## ActionNetworkTests.test_slow_query_keeps_command_queue_live_and_cancels_on_close.close()

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

## ActionRenderingTests.test_panel_states_and_resized_refresh_hit(self)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
의존성 가져오기 import pygame
의존성 가져오기 from render import Renderer
실행 pygame.display.init()
실행 pygame.font.init()
시도:
  설정 renderer ← Renderer(pygame.display.set_mode((1100, 880)))
  설정 state ← VillageState(phase='connected', own=player())
  설정 panel ← renderer.actions
  설정 panel.opened ← True
  반복 (data, message, expected) ← ((read_actions(snapshot()), 'done', '고유 행동 수  10건'), ({'available': False, 'summary': None}, 'missing', '행동 집계가 아직 없습니다'), (None, '다시 로그인해 주세요.', '다시 로그인해 주세요.')):
    설정 labels ← []
    설정 original ← renderer.text
    내부 함수 record 정의 → 아래 별도 시그니처 문서 참조
    설정 renderer.text ← record
    설정 panel.response ← {'json': data, 'message': message}
    실행 panel.draw(renderer)
    설정 renderer.text ← original
    실행 self.assertIn(expected, labels)
    조건 data is None or not data['available'] 이면:
      실행 self.assertFalse(any(('고유 행동 수' in line for line in labels)))
  반복 size ← ((1100, 880), (800, 640), (550, 440)):
    설정 renderer.screen ← pygame.display.set_mode(size)
    실행 renderer.draw(state, '', '', None, 60)
    설정 (viewport, offset) ← renderer.viewport()
    설정 (x, y) ← panel.controls()['actions_refresh'].center
    설정 point ← (offset[0] + x * viewport[0] / 1100, offset[1] + y * viewport[1] / 880)
    실행 self.assertEqual(renderer.hit_test(point), 'actions_refresh')
항상 정리:
  실행 pygame.quit()
```

직접 호출 (내부 구현을 펼치지 않음):

```text
Renderer
VillageState
any
panel.controls
panel.draw
player
pygame.display.init
pygame.display.set_mode
pygame.font.init
pygame.quit
read_actions
renderer.draw
renderer.hit_test
renderer.viewport
self.assertEqual
self.assertFalse
self.assertIn
snapshot
```
