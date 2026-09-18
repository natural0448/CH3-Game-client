# http_client.py

## 계층과 책임

HTTP 전송 — 전달받은 세션으로 timeout/redirect/status/Content-Type/크기를 검사하고 JSON만 반환한다. UI 및 게임 상태를 알지 않는다.

원문: `Game-client/http_client.py`. 호출 경계는 아래 직접 의존성까지만 기술합니다.

## 직접 의존성

```text
import aiohttp
import json
```

## 변수·상수와 출처

인스턴스/지역 변수는 각 함수 의사코드의 설정식이 출처입니다. 필드 갱신은 해당 메서드 항목에만 기록합니다.

```text
클래스 ProtocolError / 기반 Exception
```

## ProtocolError.__init__(self, message, status=None)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.
- `message`: 호출자가 전달하는 `message`; 값의 사용과 직접 호출 출처는 아래 의사코드에 표시.
- `status`: 호출자가 전달하는 `status`; 값의 사용과 직접 호출 출처는 아래 의사코드에 표시.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
실행 super().__init__(message)
설정 self.status ← status
```

직접 호출 (내부 구현을 펼치지 않음):

```text
super
super().__init__
```

## request_json(session, base, http_timeout, method, path, *, payload=None, csrf=False, csrf_token=None)

비동기 함수: worker loop 또는 테스트 loop에서 await한다.

파라미터:
- `session`: NetworkWorker가 소유한 기존 aiohttp ClientSession.
- `base`: 검증한 server_base_url origin.
- `http_timeout`: config의 http_timeout_seconds; 기본 8초.
- `method`: 호출자가 지정한 HTTP method; 통계는 GET만 사용.
- `path`: 고정 API 경로 또는 호출자가 지정한 로컬 경로.
- `payload`: 호출자가 제공한 HTTP JSON body; GET에서는 None.
- `csrf`: POST 인증 헤더를 붙일지 나타내는 bool; 기본 False.
- `csrf_token`: worker 메모리에만 보관하는 최신 CSRF; 저장/표시 금지.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
조건 session is None 이면:
  실패 전달 ProtocolError('먼저 로그인해 주세요.')
설정 headers ← {'Accept': 'application/json'}
조건 csrf 이면:
  실행 headers.update({'X-CSRFToken': csrf_token, 'Origin': base})
비동기 자원 범위 session.request(method, base + path, json=payload, headers=headers, allow_redirects=False, timeout=aiohttp.ClientTimeout(total=http_timeout)) → response:
  설정 status ← response.status
  조건 status != 200 이면:
    조건 status == 404 and path.startswith('/api/auth/') 이면:
      실패 전달 ProtocolError(f'서버에 {path} JSON API가 없어요. 서버는 변경하지 않았습니다.')
    조건 status in (301, 302, 303, 307, 308) 이면:
      실패 전달 ProtocolError('다시 로그인해 주세요. 로그인 페이지로 이동하는 응답을 받았어요.', status)
    조건 status in (401, 403) 이면:
      실패 전달 ProtocolError('다시 로그인해 주세요. 로그인 정보 또는 세션·CSRF 인증을 확인해 주세요.', status)
    실패 전달 ProtocolError(f'API 응답 오류 (HTTP {status}).', status)
  조건 response.content_type != 'application/json' 이면:
    실패 전달 ProtocolError('JSON API가 HTML 등 다른 형식으로 응답했어요.', status)
  설정 raw ← bytearray()
  반복 chunk ← response.content.iter_chunked(8192):
    실행 raw.extend(chunk)
    조건 len(raw) > 65536 이면:
      실패 전달 ProtocolError('API 응답 크기가 제한을 초과했어요.')
  시도:
    설정 data ← json.loads(raw)
  예외 (ValueError, UnicodeError):
    실패 전달 ProtocolError('API의 JSON 형식이 올바르지 않아요.')
  조건 not isinstance(data, dict) 이면:
    실패 전달 ProtocolError('API는 JSON 객체를 반환해야 해요.')
  반환 data
```

직접 호출 (내부 구현을 펼치지 않음):

```text
ProtocolError
aiohttp.ClientTimeout
bytearray
headers.update
isinstance
json.loads
len
path.startswith
raw.extend
response.content.iter_chunked
session.request
```
