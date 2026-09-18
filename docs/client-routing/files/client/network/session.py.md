# client/network/session.py

## 책임과 상태

계정 단위의 유일한 `ClientSession`, CookieJar, CSRF와 인증 순서를 소유한다. base/ws URL은 `config.server_base_url`에서 온다.

## 함수와 메서드

`server_urls(base)` — credential/path 없는 http(s) origin을 검증하고 같은 host의 `/ws/play/` ws(s) URL을 반환한다.

`AuthSession.__init__(self, config)` — URL과 0..30초 HTTP timeout을 검증한다.

`AuthSession.open(self)` — 기존 session을 닫고 메모리 CookieJar와 `JsonHttpClient`를 한 개 만든다.

`AuthSession.close(self)` — cookie jar를 지우고 session을 닫고 CSRF 참조를 비운다.

`AuthSession.request_json(self, method, path, *, payload=None, csrf=False)` — 같은 JsonHttpClient에 최신 CSRF 사용 여부를 전달한다.

`AuthSession.refresh_csrf(self)` — GET `/api/auth/csrf/` 결과를 `read_csrf`로 검증한다.

`AuthSession.login(self, username, password)`

```text
open → CSRF → POST /api/auth/login/ → CSRF 재조회 → GET /api/player/
read_login/read_state 검증
공개 Identity 반환
```

`AuthSession.logout(self)` — 최신 CSRF를 받은 뒤 Origin 포함 POST `/api/auth/logout/`을 확인한다.

직접 호출: aiohttp `ClientSession/CookieJar`, `JsonHttpClient`, auth/game contracts.
