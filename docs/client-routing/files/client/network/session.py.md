# client/network/session.py

기존 worker-owned AuthSession과 하나의 aiohttp.ClientSession/CookieJar를 재사용한다. base_url/ws_url은 server_urls가 구성한다. timeout은 config의 `http_timeout_seconds`를 float로 변환한 값이며 허용 범위는 `0 < timeout <= 30`초, 기본값은 8초다. csrf는 refresh_csrf의 현재 토큰이며 비밀값은 문서·queue에 넣지 않는다. AdEventRejected는 ProtocolError 하위 클래스이고 event_rejected=True다. post_ad_event는 길이1..128의 결정 ID와 허용 종류를 검사하고 기존 CSRF 갱신 후 같은 세션으로 POST한다.302/401 재로그인,400/403/404 영구 거절,그 외 오류는 기존 임시 실패다. read_ad_event로 공개 receipt를 검사한다.

광고 사건의 직접 HTTP 경계는 config의 `server_base_url`로 정해지는 게임 서버다. `post_ad_event`는 `refresh_csrf`로 `GET /api/auth/csrf/`를 수행한 뒤 `POST /api/ads/events/`에 `decision_id`, `event_type`만 전송한다. 로그인 쿠키와 현재 CSRF는 기존 AuthSession 내부에서 사용한다. 매체 서버의 `/api/media/events/` 중계와 사건 저장은 이 계층의 직접 호출이 아니다.

직접 호출 기대 계약: `JsonHttpClient` 생성자는 열린 ClientSession과 게임 origin을 사용하는 HTTP helper를 만들며 `request_json`은 공개 dict 또는 ProtocolError/network 예외를 반환한다. `read_csrf`는 메모리에 보관할 토큰 문자열, `read_state`는 공개 Player state dict, `read_ad_event`는 event_id/event_type/created dict를 반환한다. `read_login`은 로그인 성공 형식을 검증하며 성공 시 None, 실패 시 ValueError다. `Identity`는 검증한 Player 정보와 첫 state를 묶는다. `aiohttp.ClientSession`·`CookieJar`·`ClientTimeout`은 세션·쿠키 저장소·timeout 객체를 만들고 `session.close`와 `cookie_jar.clear`는 해당 자원을 정리한다. `urlsplit`/`urlunsplit`은 origin·WebSocket URL 구성에, `ip_address(...).is_loopback`은 로컬 IP의 cookie 정책 결정에 사용한다.

## `class AdEventRejected(ProtocolError)`

기반클래스: ProtocolError; 필드 초기값/소유자는파일설명과메서드에서정한다.

## `server_urls(base)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| base | 없음 | 경로/계정정보없는http(s) origin. |

반환·실패: (origin,websocket) tuple[str,str]; 잘못된 설정ValueError.

의사코드: origin·scheme·host·경로/계정정보 검사 → HTTP origin/ws URL 구성.

직접 호출: `ValueError`, `urlsplit`, `urlunsplit`.

## `class AuthSession`

명시적 기반클래스 없음(object 기본 상속). 필드 초기값/소유자는 파일설명과 메서드에서 정한다.

## `AuthSession.__init__(self, config)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |
| config | 없음 | 현재configuration의창/연결설정dict. |

반환·실패: None.

의사코드: 기존생성자입력에서owned상태/멤버 초기화.

직접 호출: `ValueError`, `config.get`, `float`, `server_urls`.

## `AuthSession.open(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |

반환·실패: async None.

의사코드: 이전세션정리 → loopback기반cookie정책 → ClientSession/JsonHttpClient 생성.

직접 호출: `JsonHttpClient`, `aiohttp.ClientSession`, `aiohttp.ClientTimeout`, `aiohttp.CookieJar`, `ip_address`, `self.close`, `urlsplit`.

## `AuthSession.close(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |

반환·실패: async None.

의사코드: cookie clear/session close → session/http/csrf=None.

직접 호출: `self.session.close`, `self.session.cookie_jar.clear`.

## `AuthSession.request_json(self, method, path, *, payload=None, csrf=False)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |
| method | 없음 | HTTP메서드 문자열. |
| path | 없음 | 공개HTTP경로/신뢰된PNG경로. |
| payload | None | JSON공개본문 또는None. |
| csrf | False | 해당함수/fixture에 전달되는공개입력. 실제호출범위에서검사한다. |

반환·실패: async 공개dict 또는ProtocolError/network예외.

의사코드: 열린HTTP계층 검사 → 현재CSRF선택적전달 → JsonHttpClient.

직접 호출: `ProtocolError`, `self.http.request_json`.

## `AuthSession.refresh_csrf(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |

반환·실패: async None; 잘못된API ProtocolError.

의사코드: GET 기존csrfAPI → read_csrf → 메모리token 갱신.

직접 호출: `ProtocolError`, `read_csrf`, `self.request_json`.

## `AuthSession.login(self, username, password)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |
| username | 없음 | 로그인입력; 결과queue에는넣지않는다. |
| password | 없음 | 로그인비밀입력; 실제값은문서화하지않는다. |

반환·실패: async Identity; ProtocolError/network예외.

의사코드: 기존세션새로열기 → CSRF/로그인 → CSRF갱신 → 현재Player/state계약검사.

직접 호출: `Identity`, `ProtocolError`, `read_login`, `read_state`, `self.open`, `self.refresh_csrf`, `self.request_json`.

## `AuthSession.logout(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |

반환·실패: async None 또는ProtocolError.

의사코드: 세션없으면종료 → CSRF/logout POST → authenticatedFalse 검사.

직접 호출: `ProtocolError`, `result.get`, `self.refresh_csrf`, `self.request_json`.

## `AuthSession.post_ad_event(self, decision_id: str, event_type: str) -> dict`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |
| decision_id | 없음 | 결정ID문자열1..128. |
| event_type | 없음 | impression/click 문자열. |

반환·실패: async 공개 receipt dict; AdEventRejected/ProtocolError/ValueError/network 예외.

의사코드: ID1..128/type → 기존CSRF 갱신 → 같은 게임 세션으로 `/api/ads/events/` POST → 영구거절 분류 → event_id가 `decision_id:event_type`이고 event_type/created가 계약과 일치하는 공개 receipt 반환.

직접 호출: `AdEventRejected`, `ValueError`, `isinstance`, `len`, `read_ad_event`, `self.refresh_csrf`, `self.request_json`, `str`.

## 상태·값 출처

지역 변수는 입력·기존 설정·검증한 공개응답·monotonic시간 또는 자기fixture에서 얻으며 해당함수/클래스가 쓴다. 전역/타이머/큐/fixture의 주요 초기값과 쓰기 소유자는 위 파일설명에 기록한다. 실제env값·계정암호·cookie·CSRF토큰은기록하지않는다.
