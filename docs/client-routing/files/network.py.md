# network.py

## 계층과 책임

네트워크 조정 — 하나의 thread/asyncio loop/ClientSession을 소유한다. 로그인·WS·GET 작업과 종료를 조정한다. Pygame 호출을 하지 않는다.

원문: `Game-client/network.py`. 호출 경계는 아래 직접 의존성까지만 기술합니다.

## 직접 의존성

```text
from analytics_data import API_RESPONSE_FIELDS, read_analytics, read_actions
from history_data import read_history
from http_client import ProtocolError, request_json
from state import ERROR_MESSAGES, read_snapshot, read_state
from urllib.parse import urlsplit, urlunsplit
import aiohttp
import asyncio
import json
import queue
import threading
import time
```

## 변수·상수와 출처

인스턴스/지역 변수는 각 함수 의사코드의 설정식이 출처입니다. 필드 갱신은 해당 메서드 항목에만 기록합니다.

```text
클래스 NetworkWorker / 기반 없음
```

## server_urls(base)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `base`: 검증한 server_base_url origin.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 parts ← urlsplit(base)
조건 parts.scheme not in ('http', 'https') or not parts.hostname or parts.username or parts.password or (parts.path not in ('', '/')) or parts.query or parts.fragment 이면:
  실패 전달 ValueError('server_base_url must be an http(s) origin without a path or credentials')
설정 base ← urlunsplit((parts.scheme, parts.netloc, '', '', ''))
설정 websocket ← urlunsplit(('wss' if parts.scheme == 'https' else 'ws', parts.netloc, '/ws/play/', '', ''))
반환 (base, websocket)
```

직접 호출 (내부 구현을 펼치지 않음):

```text
ValueError
urlsplit
urlunsplit
```

## NetworkWorker.__init__(self, config)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.
- `config`: configuration.load_config()가 읽은 설정 dict.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 (self.base, self.ws_url) ← server_urls(config['server_base_url'])
설정 self.http_timeout ← float(config.get('http_timeout_seconds', 8))
설정 self.command_timeout ← float(config.get('command_timeout_seconds', 8))
조건 not 0 < self.http_timeout <= 30 or not 0 < self.command_timeout <= 30 이면:
  실패 전달 ValueError('timeouts must be between 0 and 30 seconds')
설정 self.requests ← queue.Queue(maxsize=8)
설정 self.events ← queue.Queue()
설정 self.thread ← threading.Thread(target=self._thread_main, name='village-network')
설정 self._stop ← threading.Event()
설정 self.loop, self.main_task, self.ws_task, self.session, self.ws ← None
설정 self.identity ← None
설정 self.room_id ← None
설정 self.version ← -1
설정 self.csrf ← None
설정 self.ready ← False
설정 self.pending ← None
설정 self.sent_at ← float('-inf')
설정 self.epoch ← 0
설정 self._started ← False
설정 self.delivery_task ← None
설정 self.analytics_task ← None
설정 self.history_task ← None
설정 self.actions_task ← None
설정 self.delivery_sent_at ← float('-inf')
```

직접 호출 (내부 구현을 펼치지 않음):

```text
ValueError
config.get
float
queue.Queue
server_urls
threading.Event
threading.Thread
```

## NetworkWorker.start(self)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
조건 self._started 이면:
  실패 전달 RuntimeError('The network worker can only be started once')
설정 self._started ← True
실행 self.thread.start()
```

직접 호출 (내부 구현을 펼치지 않음):

```text
RuntimeError
self.thread.start
```

## NetworkWorker.submit(self, request)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.
- `request`: app이 요청 큐에 넣은 dict; kind/request_id/player_id 또는 명령.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
조건 self._stop.is_set() 이면:
  반환 False
시도:
  실행 self.requests.put_nowait(dict(request))
  반환 True
예외 queue.Full:
  반환 False
```

직접 호출 (내부 구현을 펼치지 않음):

```text
dict
self._stop.is_set
self.requests.put_nowait
```

## NetworkWorker.stop(self)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
실행 self._stop.set()
조건 self.loop and self.main_task and (not self.loop.is_closed()) 이면:
  시도:
    실행 self.loop.call_soon_threadsafe(self.main_task.cancel)
  예외 RuntimeError:
    추가 동작 없음
```

직접 호출 (내부 구현을 펼치지 않음):

```text
self._stop.set
self.loop.call_soon_threadsafe
self.loop.is_closed
```

## NetworkWorker._emit(self, kind, **data)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.
- `kind`: app/network가 사용하는 고정 요청·결과 종류.
- `data`: 호출자가 전달한 JSON 객체; 이 함수가 허용 필드를 검증.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
실행 self.events.put({'kind': kind, **data})
```

직접 호출 (내부 구현을 펼치지 않음):

```text
self.events.put
```

## NetworkWorker._status(self, phase, message)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.
- `phase`: 호출자가 전달하는 `phase`; 값의 사용과 직접 호출 출처는 아래 의사코드에 표시.
- `message`: 호출자가 전달하는 `message`; 값의 사용과 직접 호출 출처는 아래 의사코드에 표시.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
실행 self._emit('status', phase=phase, message=message, epoch=self.epoch)
```

직접 호출 (내부 구현을 펼치지 않음):

```text
self._emit
```

## NetworkWorker._thread_main(self)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
시도:
  실행 asyncio.run(self._run())
예외 asyncio.CancelledError:
  추가 동작 없음
예외 Exception:
  실행 self._emit('notice', message='네트워크 작업이 종료됐어요. 접속기를 다시 열어 주세요.')
항상 정리:
  실행 self._emit('stopped')
```

직접 호출 (내부 구현을 펼치지 않음):

```text
asyncio.run
self._emit
self._run
```

## NetworkWorker._run(self)

비동기 함수: worker loop 또는 테스트 loop에서 await한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 self.loop ← asyncio.get_running_loop()
설정 self.main_task ← asyncio.current_task()
시도:
  반복 not self._stop.is_set():
    시도:
      설정 request ← self.requests.get_nowait()
    예외 queue.Empty:
      조건 self.pending and time.monotonic() - self.sent_at > self.command_timeout 이면:
        설정 self.ready ← False
        실행 self._status('disconnected', '응답 시간이 초과됐어요. 서버 상태를 다시 확인합니다.')
        조건 self.ws 이면:
          실행 await self.ws.close()
        설정 self.pending ← None
      실행 await asyncio.sleep(0.01)
      다음 반복으로
    시도:
      설정 kind ← request.get('kind')
      조건 kind == 'login' 이면:
        실행 await self._login(request)
      그 외:
        조건 kind == 'logout' 이면:
          실행 await self._logout()
        그 외:
          조건 kind == 'command' 이면:
            실행 await self._command(request)
          그 외:
            조건 kind == 'delivery' 이면:
              조건 self.delivery_task is None or self.delivery_task.done() 이면:
                설정 self.delivery_task ← asyncio.create_task(self._delivery())
            그 외:
              조건 kind in ('analytics', 'history', 'actions') 이면:
                설정 task_name ← kind + '_task'
                설정 task ← getattr(self, task_name)
                조건 task is None or task.done() 이면:
                  설정 handler ← getattr(self, '_' + kind)
                  실행 setattr(self, task_name, asyncio.create_task(handler(dict(request))))
    예외 (ProtocolError, aiohttp.ClientError, asyncio.TimeoutError, ValueError):
      실행 self._emit('notice', message='요청을 완료하지 못했어요. 연결과 API 상태를 확인하세요.')
    항상 정리:
      실행 request.clear()
항상 정리:
  실행 await self._close_ws()
  실행 await self._close_session()
  반복 True:
    시도:
      실행 self.requests.get_nowait().clear()
    예외 queue.Empty:
      반복 종료
```

직접 호출 (내부 구현을 펼치지 않음):

```text
asyncio.create_task
asyncio.current_task
asyncio.get_running_loop
asyncio.sleep
dict
getattr
handler
request.clear
request.get
self._close_session
self._close_ws
self._command
self._delivery
self._emit
self._login
self._logout
self._status
self._stop.is_set
self.delivery_task.done
self.requests.get_nowait
self.requests.get_nowait().clear
self.ws.close
setattr
task.done
time.monotonic
```

## NetworkWorker._close_ws(self)

비동기 함수: worker loop 또는 테스트 loop에서 await한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 self.ready ← False
설정 self.pending ← None
조건 self.ws_task 이면:
  실행 self.ws_task.cancel()
  실행 await asyncio.gather(self.ws_task, return_exceptions=True)
  설정 self.ws_task ← None
조건 self.ws and (not self.ws.closed) 이면:
  실행 await self.ws.close()
설정 self.ws ← None
```

직접 호출 (내부 구현을 펼치지 않음):

```text
asyncio.gather
self.ws.close
self.ws_task.cancel
```

## NetworkWorker._close_session(self)

비동기 함수: worker loop 또는 테스트 loop에서 await한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
반복 name ← ('history_task', 'analytics_task', 'actions_task', 'delivery_task'):
  설정 task ← getattr(self, name)
  조건 task 이면:
    실행 task.cancel()
    실행 await asyncio.gather(task, return_exceptions=True)
    실행 setattr(self, name, None)
조건 self.session 이면:
  실행 self.session.cookie_jar.clear()
  실행 await self.session.close()
설정 self.session ← None
설정 self.csrf, self.identity ← None
설정 self.room_id ← None
설정 self.version ← -1
설정 self.delivery_sent_at ← float('-inf')
```

직접 호출 (내부 구현을 펼치지 않음):

```text
asyncio.gather
float
getattr
self.session.close
self.session.cookie_jar.clear
setattr
task.cancel
```

## NetworkWorker._json(self, method, path, *, payload=None, csrf=False)

비동기 함수: worker loop 또는 테스트 loop에서 await한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.
- `method`: 호출자가 지정한 HTTP method; 통계는 GET만 사용.
- `path`: 고정 API 경로 또는 호출자가 지정한 로컬 경로.
- `payload`: 호출자가 제공한 HTTP JSON body; GET에서는 None.
- `csrf`: POST 인증 헤더를 붙일지 나타내는 bool; 기본 False.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
반환 await request_json(self.session, self.base, self.http_timeout, method, path, payload=payload, csrf=csrf, csrf_token=self.csrf)
```

직접 호출 (내부 구현을 펼치지 않음):

```text
request_json
```

## NetworkWorker._get_csrf(self)

비동기 함수: worker loop 또는 테스트 loop에서 await한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 data ← await self._json('GET', '/api/auth/csrf/')
설정 token ← data.get('csrfToken', data.get('csrf_token'))
조건 not isinstance(token, str) or not token or len(token) > 256 이면:
  실패 전달 ProtocolError('CSRF API에 csrfToken 문자열이 필요해요.')
설정 self.csrf ← token
```

직접 호출 (내부 구현을 펼치지 않음):

```text
ProtocolError
data.get
isinstance
len
self._json
```

## NetworkWorker._delivery(self)

비동기 함수: worker loop 또는 테스트 loop에서 await한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 player_id ← self.identity
설정 result ← dict(player_id=player_id, path='GET /api/delivery/', status=None, json=None)
시도:
  조건 self.session is None or player_id is None 이면:
    실패 전달 ProtocolError('먼저 로그인해 주세요.')
  설정 now ← time.monotonic()
  조건 now - self.delivery_sent_at < 5 이면:
    실패 전달 ProtocolError('전달 상태 조회는 5초 간격으로 할 수 있어요.')
  설정 self.delivery_sent_at ← now
  설정 data ← await self._json('GET', '/api/delivery/')
  설정 result['status'] ← 200
  설정 counts ← (data.get('event_count'), data.get('pending_publish_count'))
  조건 any((type(value) is not int or value < 0 for value in counts)) or data.get('source') != 'mysql-outbox' 이면:
    실패 전달 ProtocolError('이벤트 전달 상태의 응답 형식을 확인해 주세요.')
  설정 result['json'] ← {key: data[key] for key in API_RESPONSE_FIELDS['/api/delivery/']}
  설정 result['message'] ← '마지막 조회 결과 · 자동 갱신 없음'
예외 ProtocolError → exc:
  설정 result['status'] ← exc.status if exc.status is not None else result['status']
  설정 result['message'] ← str(exc)
예외 (aiohttp.ClientError, asyncio.TimeoutError, ValueError):
  설정 result['message'] ← '조회에 실패했어요. 서버 연결을 확인하고 다시 눌러 주세요.'
실행 self._emit('delivery', **result)
```

직접 호출 (내부 구현을 펼치지 않음):

```text
ProtocolError
any
data.get
dict
self._emit
self._json
str
time.monotonic
type
```

## NetworkWorker._player(self)

비동기 함수: worker loop 또는 테스트 loop에서 await한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 data ← await self._json('GET', '/api/player/')
설정 state ← read_state(data)
조건 self.identity is not None and state['player_id'] != self.identity 이면:
  실패 전달 ProtocolError('로그인 계정과 응답의 플레이어가 일치하지 않아요.')
설정 safe ← {'type': 'state', **state}
반환 safe
```

직접 호출 (내부 구현을 펼치지 않음):

```text
ProtocolError
read_state
self._json
```

## NetworkWorker._read_panel(self, request, *, kind, path, parser, empty_message)

비동기 함수: worker loop 또는 테스트 loop에서 await한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.
- `request`: app이 요청 큐에 넣은 dict; kind/request_id/player_id 또는 명령.
- `kind`: app/network가 사용하는 고정 요청·결과 종류.
- `path`: 고정 API 경로 또는 호출자가 지정한 로컬 경로.
- `parser`: JSON에서 안전한 표시 dict를 반환하는 검증 함수.
- `empty_message`: 정상 미생성/빈 응답에서 보여 줄 고정 문구.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 identity ← self.identity
설정 result ← dict(player_id=identity, request_id=request.get('request_id'), path='GET ' + path, status=None, json=None)
시도:
  조건 self.session is None or identity is None or request.get('player_id') != identity 이면:
    실패 전달 ProtocolError('먼저 로그인해 주세요.')
  설정 data ← await self._json('GET', path)
  설정 result['status'] ← 200
  설정 result['json'] ← parser(data)
  설정 safe ← result['json']
  설정 present ← bool(safe.get('events')) if kind == 'history' else safe.get('available')
  설정 result['message'] ← '마지막 조회 결과 · 버튼으로만 갱신' if present else empty_message
예외 ProtocolError → exc:
  설정 result['status'] ← exc.status if exc.status is not None else result['status']
  설정 result['message'] ← str(exc)
예외 (ValueError, TypeError, KeyError, AttributeError, OverflowError):
  설정 result['message'] ← '조회 응답의 필드와 형식을 확인해 주세요.'
예외 (aiohttp.ClientError, asyncio.TimeoutError):
  설정 result['message'] ← '조회하지 못했어요. 서버 연결을 확인하고 다시 눌러 주세요.'
실행 self._emit(kind, **result)
```

직접 호출 (내부 구현을 펼치지 않음):

```text
ProtocolError
bool
dict
parser
request.get
safe.get
self._emit
self._json
str
```

## NetworkWorker._analytics(self, request)

비동기 함수: worker loop 또는 테스트 loop에서 await한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.
- `request`: app이 요청 큐에 넣은 dict; kind/request_id/player_id 또는 명령.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
실행 await self._read_panel(request, kind='analytics', path='/api/analytics/', parser=read_analytics, empty_message='아직 첫 집계가 없습니다')
```

직접 호출 (내부 구현을 펼치지 않음):

```text
self._read_panel
```

## NetworkWorker._actions(self, request)

비동기 함수: worker loop 또는 테스트 loop에서 await한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.
- `request`: app이 요청 큐에 넣은 dict; kind/request_id/player_id 또는 명령.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
실행 await self._read_panel(request, kind='actions', path='/api/analytics/actions/', parser=read_actions, empty_message='행동 집계가 아직 없습니다')
```

직접 호출 (내부 구현을 펼치지 않음):

```text
self._read_panel
```

## NetworkWorker._history(self, request)

비동기 함수: worker loop 또는 테스트 loop에서 await한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.
- `request`: app이 요청 큐에 넣은 dict; kind/request_id/player_id 또는 명령.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 identity ← self.identity
실행 await self._read_panel(request, kind='history', path='/api/history/', parser=lambda data: read_history(data, identity), empty_message='아직 행동 기록이 없습니다')
```

직접 호출 (내부 구현을 펼치지 않음):

```text
read_history
self._read_panel
```

## NetworkWorker._login(self, request)

비동기 함수: worker loop 또는 테스트 loop에서 await한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.
- `request`: app이 요청 큐에 넣은 dict; kind/request_id/player_id 또는 명령.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
실행 await self._close_ws()
실행 await self._close_session()
실행 self._status('authenticating', '로그인 확인 중…')
설정 self.session ← aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar(unsafe=True), timeout=aiohttp.ClientTimeout(total=self.http_timeout))
시도:
  실행 await self._get_csrf()
  설정 result ← await self._json('POST', '/api/auth/login/', payload={'username': request.pop('username', ''), 'password': request.pop('password', '')}, csrf=True)
  조건 result.get('authenticated') is not True 이면:
    실패 전달 ProtocolError('서버가 로그인 성공을 확인하지 않았어요.')
  실행 await self._get_csrf()
  설정 data ← await self._player()
  설정 self.identity ← data['player_id']
  설정 self.room_id ← data['room_id']
  설정 self.version ← data['version']
  실행 self._emit('identity', data=data)
  설정 self.ws_task ← asyncio.create_task(self._websockets())
예외 ProtocolError → exc:
  실행 await self._close_session()
  실행 self._emit('login_failed', message=str(exc))
예외 (aiohttp.ClientError, asyncio.TimeoutError, ValueError):
  실행 await self._close_session()
  실행 self._emit('login_failed', message='서버에 연결하지 못했어요. 서버 실행과 주소를 확인하세요.')
```

직접 호출 (내부 구현을 펼치지 않음):

```text
ProtocolError
aiohttp.ClientSession
aiohttp.ClientTimeout
aiohttp.CookieJar
asyncio.create_task
request.pop
result.get
self._close_session
self._close_ws
self._emit
self._get_csrf
self._json
self._player
self._status
self._websockets
str
```

## NetworkWorker._logout(self)

비동기 함수: worker loop 또는 테스트 loop에서 await한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
실행 self._status('logging_out', '연결을 닫고 로그아웃하는 중…')
실행 await self._close_ws()
설정 message ← '로그아웃했어요.'
시도:
  조건 self.session 이면:
    실행 await self._get_csrf()
    설정 result ← await self._json('POST', '/api/auth/logout/', payload={}, csrf=True)
    조건 result.get('authenticated') is not False 이면:
      실패 전달 ProtocolError('서버 로그아웃 확인이 필요해요.')
예외 (ProtocolError, aiohttp.ClientError, asyncio.TimeoutError, ValueError):
  설정 message ← '서버 로그아웃을 확인하지 못했어요. 이 접속기의 계정 정보는 지웠습니다.'
항상 정리:
  실행 await self._close_session()
  실행 self._emit('logged_out', message=message)
```

직접 호출 (내부 구현을 펼치지 않음):

```text
ProtocolError
result.get
self._close_session
self._close_ws
self._emit
self._get_csrf
self._json
self._status
```

## NetworkWorker._command(self, request)

비동기 함수: worker loop 또는 테스트 loop에서 await한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.
- `request`: app이 요청 큐에 넣은 dict; kind/request_id/player_id 또는 명령.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 command ← request['command']
설정 delay ← 0.2 - (time.monotonic() - self.sent_at)
조건 delay > 0 이면:
  실행 await asyncio.sleep(delay)
조건 not self.ready or not self.ws or self.ws.closed or self.pending or (request.get('epoch') != self.epoch) 이면:
  설정 self.ready ← False
  실행 self._status('disconnected', '전송할 수 없는 상태예요. 서버 상태를 다시 확인합니다.')
  조건 self.ws 이면:
    실행 await self.ws.close()
  반환 None
설정 self.pending ← command['command_id']
설정 self.sent_at ← time.monotonic()
시도:
  실행 await self.ws.send_json(command)
예외 (aiohttp.ClientError, ConnectionError, RuntimeError):
  설정 self.ready ← False
  실행 self._status('disconnected', '연결이 끊겼어요. 전송 중 행동은 다시 보내지 않습니다.')
  실행 await self.ws.close()
```

직접 호출 (내부 구현을 펼치지 않음):

```text
asyncio.sleep
request.get
self._status
self.ws.close
self.ws.send_json
time.monotonic
```

## NetworkWorker._websockets(self)

비동기 함수: worker loop 또는 테스트 loop에서 await한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 retries ← 0
반복 True:
  조건 retries 이면:
    실행 self._status('reconnecting', f'연결 끊김 · 2초 뒤 재연결 {retries}/3')
    실행 await asyncio.sleep(2)
  갱신 self.epoch += 1
  실행 self._status('connecting', '서버의 첫 상태를 기다리는 중…')
  설정 first ← True
  시도:
    설정 self.ws ← await self.session.ws_connect(self.ws_url, origin=self.base, heartbeat=5, timeout=aiohttp.ClientWSTimeout(ws_close=2), max_msg_size=65536)
    반복 True:
      조건 first 이면:
        설정 message ← await asyncio.wait_for(self.ws.receive(), self.http_timeout)
      그 외:
        설정 message ← await self.ws.receive()
      조건 message.type != aiohttp.WSMsgType.TEXT 이면:
        반복 종료
      설정 data ← json.loads(message.data)
      조건 not isinstance(data, dict) 이면:
        실패 전달 ValueError('invalid_message')
      조건 data.get('type') == 'state' 이면:
        설정 state ← read_state(data)
        조건 state['room_id'] != self.room_id 이면:
          다음 반복으로
        설정 mine ← state['player_id'] == self.identity
        조건 mine and state['version'] < self.version 이면:
          다음 반복으로
        조건 mine 이면:
          설정 self.version ← state['version']
        설정 safe ← {'type': 'state', **state}
        설정 command_id ← data.get('command_id')
        조건 isinstance(command_id, str) and len(command_id) <= 64 이면:
          설정 safe['command_id'] ← command_id
        조건 mine and command_id and (command_id == self.pending) 이면:
          설정 self.pending ← None
        실행 self._emit('state', data=safe, epoch=self.epoch, first=first and mine)
        조건 mine 이면:
          설정 self.ready ← True
          설정 first ← False
          설정 retries ← 0
      그 외:
        조건 data.get('type') == 'snapshot' 이면:
          설정 members ← read_snapshot(data)
          설정 safe ← {'type': 'snapshot', 'players': [{'type': 'state', **player} for player in members.values() if player['room_id'] == self.room_id]}
          실행 self._emit('snapshot', data=safe, epoch=self.epoch)
        그 외:
          조건 data.get('type') == 'error' 이면:
            설정 command_id ← data.get('command_id')
            조건 command_id and command_id == self.pending 이면:
              설정 self.pending ← None
            설정 code ← data.get('code')
            실행 self._emit('error', epoch=self.epoch, code=code if isinstance(code, str) and code in ERROR_MESSAGES else 'rejected', command_id=command_id if isinstance(command_id, str) and len(command_id) <= 64 else None)
  예외 (aiohttp.ClientError, asyncio.TimeoutError, ValueError, ConnectionError):
    추가 동작 없음
  항상 정리:
    설정 self.ready ← False
    설정 self.pending ← None
    실행 self._status('disconnected', '연결이 끊겼어요. 조작을 잠시 멈춥니다.')
    조건 self.ws and (not self.ws.closed) 이면:
      실행 await self.ws.close()
    설정 self.ws ← None
  조건 retries >= 3 이면:
    실행 self._status('disconnected', '재연결 3회를 마쳤어요. 로그아웃 후 다시 로그인해 주세요.')
    반환 None
  갱신 retries += 1
```

직접 호출 (내부 구현을 펼치지 않음):

```text
ValueError
aiohttp.ClientWSTimeout
asyncio.sleep
asyncio.wait_for
data.get
isinstance
json.loads
len
members.values
read_snapshot
read_state
self._emit
self._status
self.session.ws_connect
self.ws.close
self.ws.receive
```
