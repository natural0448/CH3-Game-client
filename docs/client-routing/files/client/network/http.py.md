# client/network/http.py

## 책임과 상태

worker 소유 `ClientSession`의 공통 JSON 정책이다. `JsonHttpClient`는 session, base_url, timeout, Origin만 가진다.

## 메서드

`ProtocolError.__init__(self, message, status=None)` — credential-free 문구와 선택 HTTP status를 저장한다.

`JsonHttpClient.__init__(self, session, base_url, timeout, origin)` — AuthSession이 전달한 같은 세션과 origin을 저장한다.

`JsonHttpClient.request_json(self, method, path, *, payload=None, csrf_token=None)`

```text
열린 session 확인
Accept JSON, 필요 시 X-CSRFToken·Origin 추가
allow_redirects=False와 ClientTimeout으로 request
301..308/401/403을 로그인 안내로 분류
2xx·application/json 확인 후 최대 65536 bytes 읽기
object JSON 반환
```

직접 호출: `aiohttp.ClientTimeout`, `ClientSession.request`, `json.loads`. body·header·비밀값은 log하지 않는다.
