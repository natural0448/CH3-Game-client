# test_delivery_client.py

## 계층과 책임

회귀 검증 — 해당 기능의 오프라인 입력·기대 결과·fake session을 검증한다.

원문: `Game-client/test_delivery_client.py`. 호출 경계는 아래 직접 의존성까지만 기술합니다.

## 직접 의존성

```text
from network import NetworkWorker
from state import VillageState
from unittest.mock import patch
import asyncio
import json
import unittest
```

## 변수·상수와 출처

인스턴스/지역 변수는 각 함수 의사코드의 설정식이 출처입니다. 필드 갱신은 해당 메서드 항목에만 기록합니다.

```text
클래스 Response / 기반 없음
클래스 Session / 기반 없음
클래스 DeliveryNetworkTests / 기반 unittest.IsolatedAsyncioTestCase
클래스 DeliveryStateTests / 기반 unittest.TestCase
```

## Response.__init__(self, status=200, content_type='application/json', data=None, raw=None)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.
- `status`: 호출자가 전달하는 `status`; 값의 사용과 직접 호출 출처는 아래 의사코드에 표시.
- `content_type`: 호출자가 전달하는 `content_type`; 값의 사용과 직접 호출 출처는 아래 의사코드에 표시.
- `data`: 호출자가 전달한 JSON 객체; 이 함수가 허용 필드를 검증.
- `raw`: 호출자가 전달하는 `raw`; 값의 사용과 직접 호출 출처는 아래 의사코드에 표시.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 (self.status, self.content_type) ← (status, content_type)
설정 self.raw ← raw if raw is not None else json.dumps(data).encode()
설정 self.content ← self
설정 self.body_read ← False
```

직접 호출 (내부 구현을 펼치지 않음):

```text
json.dumps
json.dumps(data).encode
```

## Response.__aenter__(self)

비동기 함수: worker loop 또는 테스트 loop에서 await한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
반환 self
```

직접 호출 (내부 구현을 펼치지 않음):

```text
없음
```

## Response.__aexit__(self, *args)

비동기 함수: worker loop 또는 테스트 loop에서 await한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.
- `args`: 호출자가 전달하는 `args`; 값의 사용과 직접 호출 출처는 아래 의사코드에 표시.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
추가 동작 없음
```

직접 호출 (내부 구현을 펼치지 않음):

```text
없음
```

## Response.iter_chunked(self, size)

비동기 함수: worker loop 또는 테스트 loop에서 await한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.
- `size`: 호출자가 전달하는 `size`; 값의 사용과 직접 호출 출처는 아래 의사코드에 표시.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 self.body_read ← True
실행 (yield self.raw)
```

직접 호출 (내부 구현을 펼치지 않음):

```text
없음
```

## Session.__init__(self, response)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.
- `response`: worker가 허용 목록으로 만든 path/status/json/message dict.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 self.response ← response
설정 self.calls ← []
```

직접 호출 (내부 구현을 펼치지 않음):

```text
없음
```

## Session.request(self, *args, **kwargs)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.
- `args`: 호출자가 전달하는 `args`; 값의 사용과 직접 호출 출처는 아래 의사코드에 표시.
- `kwargs`: 호출자가 전달하는 `kwargs`; 값의 사용과 직접 호출 출처는 아래 의사코드에 표시.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
실행 self.calls.append((args, kwargs))
반환 self.response
```

직접 호출 (내부 구현을 펼치지 않음):

```text
self.calls.append
```

## DeliveryNetworkTests.worker(self, response)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.
- `response`: worker가 허용 목록으로 만든 path/status/json/message dict.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 worker ← NetworkWorker({'server_base_url': 'http://127.0.0.1:8000'})
설정 worker.identity ← 7
설정 worker.session ← Session(response)
반환 worker
```

직접 호출 (내부 구현을 펼치지 않음):

```text
NetworkWorker
Session
```

## DeliveryNetworkTests.test_whitelisted_result_same_session_and_five_second_limit(self)

비동기 함수: worker loop 또는 테스트 loop에서 await한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 response ← Response(data={'event_count': 12, 'pending_publish_count': 3, 'source': 'mysql-outbox', 'password': 'excluded', 'csrfToken': 'excluded'})
설정 worker ← self.worker(response)
설정 session ← worker.session
설정 worker.pending ← 'game-command'
자원 범위 patch('network.time.monotonic', return_value=100):
  실행 await worker._delivery()
설정 event ← worker.events.get_nowait()
실행 self.assertEqual(event['json'], {'event_count': 12, 'pending_publish_count': 3, 'source': 'mysql-outbox'})
실행 self.assertEqual(event['status'], 200)
실행 self.assertEqual(event['path'], 'GET /api/delivery/')
실행 self.assertIs(worker.session, session)
실행 self.assertEqual(worker.pending, 'game-command')
설정 (args, kwargs) ← session.calls[0]
실행 self.assertEqual(args, ('GET', 'http://127.0.0.1:8000/api/delivery/'))
실행 self.assertFalse(kwargs['allow_redirects'])
실행 self.assertEqual(kwargs['timeout'].total, 8)
자원 범위 patch('network.time.monotonic', return_value=104.99):
  실행 await worker._delivery()
실행 self.assertEqual(len(session.calls), 1)
실행 self.assertIsNone(worker.events.get_nowait()['json'])
자원 범위 patch('network.time.monotonic', return_value=105):
  실행 await worker._delivery()
실행 self.assertEqual(len(session.calls), 2)
```

직접 호출 (내부 구현을 펼치지 않음):

```text
Response
len
patch
self.assertEqual
self.assertFalse
self.assertIs
self.assertIsNone
self.worker
worker._delivery
worker.events.get_nowait
```

## DeliveryNetworkTests.test_redirect_unauthorized_and_html_never_parse_body(self)

비동기 함수: worker loop 또는 테스트 loop에서 await한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
반복 status ← (302, 401, 200):
  자원 범위 self.subTest(status=status):
    설정 response ← Response(status=status, content_type='text/html', raw=b'<html>private</html>')
    설정 worker ← self.worker(response)
    실행 await worker._delivery()
    설정 event ← worker.events.get_nowait()
    실행 self.assertFalse(response.body_read)
    실행 self.assertEqual(event['status'], status)
    실행 self.assertIsNone(event['json'])
    실행 self.assertNotIn('private', str(event))
    조건 status in (302, 401) 이면:
      실행 self.assertIn('로그인', event['message'])
```

직접 호출 (내부 구현을 펼치지 않음):

```text
Response
self.assertEqual
self.assertFalse
self.assertIn
self.assertIsNone
self.assertNotIn
self.subTest
self.worker
str
worker._delivery
worker.events.get_nowait
```

## DeliveryNetworkTests.test_invalid_counts_source_json_and_timeout(self)

비동기 함수: worker loop 또는 테스트 loop에서 await한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
반복 data ← ({'event_count': True, 'pending_publish_count': 0, 'source': 'mysql-outbox'}, {'event_count': 1, 'pending_publish_count': -1, 'source': 'mysql-outbox'}, {'event_count': 1, 'pending_publish_count': 0, 'source': 'private-token'}):
  설정 worker ← self.worker(Response(data=data))
  실행 await worker._delivery()
  실행 self.assertIsNone(worker.events.get_nowait()['json'])
설정 worker ← self.worker(Response(raw=b'invalid-json'))
실행 await worker._delivery()
실행 self.assertIsNone(worker.events.get_nowait()['json'])
내부 함수 timeout 정의 → 아래 별도 시그니처 문서 참조
설정 worker._json ← timeout
설정 worker.delivery_sent_at ← float('-inf')
실행 await worker._delivery()
실행 self.assertIn('실패', worker.events.get_nowait()['message'])
```

직접 호출 (내부 구현을 펼치지 않음):

```text
Response
float
self.assertIn
self.assertIsNone
self.worker
worker._delivery
worker.events.get_nowait
```

## DeliveryNetworkTests.test_invalid_counts_source_json_and_timeout.timeout(*args)

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

## DeliveryNetworkTests.test_slow_delivery_does_not_block_command_queue_and_is_cancelled_on_close(self)

비동기 함수: worker loop 또는 테스트 loop에서 await한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 worker ← self.worker(Response(data={}))
설정 (started, moved, cancelled) ← (asyncio.Event(), asyncio.Event(), asyncio.Event())
내부 함수 slow_delivery 정의 → 아래 별도 시그니처 문서 참조
내부 함수 command 정의 → 아래 별도 시그니처 문서 참조
내부 함수 close_session 정의 → 아래 별도 시그니처 문서 참조
설정 (worker._delivery, worker._command) ← (slow_delivery, command)
설정 worker.session.close ← close_session
설정 worker.session.cookie_jar ← type('Jar', (), {'clear': lambda self: None})()
설정 task ← asyncio.create_task(worker._run())
시도:
  실행 worker.submit({'kind': 'delivery'})
  실행 await asyncio.wait_for(started.wait(), 1)
  실행 worker.submit({'kind': 'command'})
  실행 await asyncio.wait_for(moved.wait(), 1)
  실행 self.assertFalse(cancelled.is_set())
항상 정리:
  실행 task.cancel()
  실행 await asyncio.gather(task, return_exceptions=True)
실행 self.assertTrue(cancelled.is_set())
실행 self.assertIsNone(worker.session)
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
self.assertFalse
self.assertIsNone
self.assertTrue
self.worker
started.wait
task.cancel
type
type('Jar', (), {'clear': lambda self: None})
worker._run
worker.submit
```

## DeliveryNetworkTests.test_slow_delivery_does_not_block_command_queue_and_is_cancelled_on_close.slow_delivery()

비동기 함수: worker loop 또는 테스트 loop에서 await한다.

파라미터:
- 없음.

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

## DeliveryNetworkTests.test_slow_delivery_does_not_block_command_queue_and_is_cancelled_on_close.command(request)

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

## DeliveryNetworkTests.test_slow_delivery_does_not_block_command_queue_and_is_cancelled_on_close.close_session()

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

## DeliveryStateTests.test_click_gating_result_isolation_and_logout_cleanup(self)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 state ← VillageState()
실행 self.assertIsNone(state.request_delivery(now=10))
설정 state.own ← {'player_id': 7, 'coins': 4}
설정 state.phase ← 'connected'
설정 state.pending ← 'move-uuid'
실행 self.assertEqual(state.request_delivery(now=10), {'kind': 'delivery'})
실행 self.assertIsNone(state.request_delivery(now=20))
실행 state.accept(dict(kind='delivery', player_id=7, path='GET /api/delivery/', status=200, json={'event_count': 12, 'pending_publish_count': 3, 'source': 'mysql-outbox'}, message='done'))
실행 self.assertEqual(state.own['coins'], 4)
실행 self.assertEqual(state.pending, 'move-uuid')
실행 self.assertIsNone(state.request_delivery(now=14.99))
실행 self.assertIsNotNone(state.request_delivery(now=15))
실행 state.clear_account()
실행 state.accept(dict(kind='delivery', player_id=7))
실행 self.assertIsNone(state.delivery)
실행 self.assertFalse(state.delivery_busy)
```

직접 호출 (내부 구현을 펼치지 않음):

```text
VillageState
dict
self.assertEqual
self.assertFalse
self.assertIsNone
self.assertIsNotNone
state.accept
state.clear_account
state.request_delivery
```
