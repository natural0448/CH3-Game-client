# client/network/session.py

## 책임과 상태

계정 단위의 유일한 `ClientSession`, CookieJar, CSRF와 인증 순서를 소유한다. base/ws URL은 `config.server_base_url`에서 온다.

## 함수와 메서드

`server_urls(base)` — credential/path 없는 http(s) origin을 검증하고 같은 host의 `/ws/play/` ws(s) URL을 반환한다.

`AuthSession.__init__(self, config)` — URL과 0..30초 HTTP timeout을 검증한다.

`AuthSession.open(self)` — 기존 session을 닫고 메모리 CookieJar와 `JsonHttpClient`를 한 개 만든다.

```text
close로 기존 계정 session 정리
base_url의 hostname을 ip_address로 해석해 is_loopback을 local_ip에 저장
IP 문자열이 아닌 hostname이면 local_ip=False
CookieJar(unsafe=local_ip)와 timeout을 사용해 ClientSession 생성
같은 session/base_url/timeout/Origin으로 JsonHttpClient 생성
```

`local_ip`는 이 메서드의 지역 bool이며 127.0.0.1·::1 같은 루프백 IP일 때만 True다. localhost 같은 DNS 이름은 기본 안전 CookieJar에서도 쿠키를 허용한다. 원격 IP는 unsafe=False다. 메서드는 None을 반환하며 session/http의 쓰기 소유자는 AuthSession이다.

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

직접 호출: aiohttp `ClientSession/CookieJar`, `JsonHttpClient`, auth/game contracts, `ipaddress.ip_address`, `urlsplit`.
