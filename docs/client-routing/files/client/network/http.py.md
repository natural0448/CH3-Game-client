# client/network/http.py

기존 bounded JSON HTTP 계층. ProtocolError.status/error_code의 기본값은None이고 message는 공개 설명이다. csrf_token이 있으면 Origin/CSRF header를 보내고 redirect는 따르지 않는다. 기존 성공 JSON 최대65536바이트 정책을 유지한다. /api/ads/events/400에서만 최대65536바이트 공개 본문을 읽으며 decision_snapshot_missing/decision_not_found_for_subject/impression_required 세 코드만 공개 설명으로 사용한다. 다른 body·잘못된 JSON·비문자열 코드는 공개 generic 거절로 처리하고 서버 trace는 전달하지 않는다. 다른 API의 기존 정책은 유지한다.

직접 호출 기대 계약: UI/상태 helper는 각 짝 문서의 반환 계약을 따른다. worker.submit은접수bool, HTTP/JSON helper는공개dict 또는공개오류, read_ad_event는id/type/created dict, emit은queue전달, create_task는Task, Pygame draw/decode는Surface/표시receipt, fixture Web은bytes이다. 하위 계층 내부를 복제하지 않는다.

## `class ProtocolError(Exception)`

기반클래스: Exception; 필드 초기값/소유자는파일설명과메서드에서정한다.

## `ProtocolError.__init__(self, message, status=None, error_code=None)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |
| message | 없음 | 공개오류설명 문자열. |
| status | None | HTTP정수 또는None. |
| error_code | None | 허용공개오류코드 문자열 또는None. |

반환·실패: None.

의사코드: Exception 초기화 → status/error_code 소유.

직접 호출: `super`, `super().__init__`.

## `class JsonHttpClient`

기반클래스: ; 필드 초기값/소유자는파일설명과메서드에서정한다.

## `JsonHttpClient.__init__(self, session, base_url, timeout, origin)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |
| session | 없음 | worker-owned aiohttp 세션. |
| base_url | 없음 | 게임HTTP origin. |
| timeout | 없음 | 응답timeout초. |
| origin | 없음 | 같은게임origin. |

반환·실패: None.

의사코드: 기존생성자입력에서owned상태/멤버 초기화.

직접 호출: .

## `JsonHttpClient.request_json(self, method, path, *, payload=None, csrf_token=None)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |
| method | 없음 | HTTP메서드 문자열. |
| path | 없음 | 공개HTTP경로/신뢰된PNG경로. |
| payload | None | JSON공개본문 또는None. |
| csrf_token | None | 세션CSRF 문자열 또는None; 메모리에서header에만사용. |

반환·실패: async dict 또는ProtocolError/network 예외.

의사코드: 현재세션/headers/timeout → request → events400공개코드 또는 기존status정책 → bounded JSON객체.

직접 호출: `ProtocolError`, `aiohttp.ClientTimeout`, `b''.join`, `chunks.append`, `data.get`, `headers.update`, `isinstance`, `json.loads`, `known.get`, `len`, `response.content.iter_chunked`, `response.content.read`, `self.session.request`.

## 상태·값 출처

지역 변수는 입력·기존 설정·검증한 공개응답·monotonic시간 또는 자기fixture에서 얻으며 해당함수/클래스가 쓴다. 전역/타이머/큐/fixture의 주요 초기값과 쓰기 소유자는 위 파일설명에 기록한다. 실제env값·계정암호·cookie·CSRF토큰은기록하지않는다.
