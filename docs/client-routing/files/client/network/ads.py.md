# client/network/ads.py

worker asyncio loop의 AdGateway. auth는 기존 AuthSession, emit은 queue 결과 sink, identity는 공개 로그인 Player 정보, generation은 계정 경계다. tasks는 슬롯 선택 및 (slot,event_type) task를 소유하며 close에서 cancel/gather/clear한다. last_requested는 슬롯별 monotonic15초 제한이다. 현재 generation의 영구 사건 거절에는 해당 선택 cooldown을 제거해 상태 계층의2초 새 선택 정책을 허용한다. 성공 result는 공개 decision/PNG 또는 id/type/created receipt만 담는다. 영구400/403/404(302/401은 재로그인)는 event_rejected=True, needs_login은302/401이다. 임시 장애/시간초과는 같은 결정을 재시도한다. PNG는 기존 동일 origin whitelist·1MiB/1024차원 상한이다.

2026-10-08 검수: 직접 선택 요청은 `AuthSession.request_json("POST", "/api/ads/decision/", payload={"slot_id": slot}, csrf=True)`다. PNG GET은 `auth.base_url + creative_path`로 같은 게임 서버 origin에 전송한다. 사건은 `AuthSession.post_ad_event(decision_id, event_type)`에 위임하며 직접 광고 서버 media API나 로컬 NDJSON 파일을 읽지 않는다. 서버 측 player snapshot 내보내기를 이 접속기의 선택·사건 경로로 취급하지 않는다.

초기 상태는 `identity=None`, `generation=0`, `tasks={}`, `last_requested={}`다. 모두 AdGateway가 worker loop에서 소유한다. 허용 슬롯·사건 종류·이미지 경로의 출처는 `client.contracts.ads`의 `SLOTS`, `EVENT_TYPES`, `CREATIVE_PATHS`이며 이 계층에서 별도로 정의하지 않는다. PNG 요청은 redirect를 허용하지 않고 total timeout=3초, read chunk=8192 bytes, 누적 크기=1048576 bytes 이하, 각 width/height=1..1024를 검사한다.

직접 호출 기대 계약: `AuthSession.request_json`은 공개 JSON dict를 반환하고 `post_ad_event`는 공개 receipt dict 또는 오류를 반환한다. `read_decision`은 검증한 선택 dict 또는 None, `read_ad_event`는 event_id/event_type/created dict를 반환한다. `auth.session.get`은 응답 context를 제공하며 `response.content.iter_chunked`는 bytes chunk를 전달한다. `asyncio.create_task`는 소유할 Task를 만들고 `asyncio.gather`는 취소한 Task의 종료를 기다린다. `emit`은 현재 generation의 공개 결과를 worker queue에 전달하는 callback이며 반환값은 사용하지 않는다. `time.monotonic`은 간격 계산용 float, `struct.unpack(">II", ...)`은 PNG width/height tuple을 반환한다.

## `class AdGateway`

명시적 기반클래스 없음(object 기본 상속). 필드 초기값/소유자는 파일설명과 메서드에서 정한다.

## `AdGateway.__init__(self, auth_session, emit)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |
| auth_session | 없음 | worker가소유한 AuthSession. |
| emit | 없음 | 공개queue event sink callable. |

반환·실패: None.

의사코드: 기존생성자입력에서owned상태/멤버 초기화.

직접 호출 없음. 입력 참조와 필드 초기값만 대입한다.

## `AdGateway.set_identity(self, identity)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |
| identity | 없음 | 현재공개게임 Identity. |

반환·실패: None.

의사코드: 현재identity 대입 → generation증가.

직접 호출 없음. identity를 대입하고 generation을 증가시킨다.

## `AdGateway.start(self, request)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |
| request | 없음 | 기존 dict queue선택/사건요청. |

반환·실패: bool.

의사코드: 허용슬롯/진행중task 검사 → 현재fetch task 생성/소유.

직접 호출: `asyncio.create_task`, `dict`, `isinstance`, `request.get`, `self.fetch`, `self.tasks[slot].done`.

## `AdGateway.fetch(self, request)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |
| request | 없음 | 기존 dict queue선택/사건요청. |

반환·실패: async None; 공개 selection queue.

의사코드: identity/15초 → 같은 게임 세션으로 `/api/ads/decision/` CSRF POST(slot_id) → read_decision의 공개 dict 또는 None 검사 → creative_path가 있으면 PNG bytes 조회 → 현재generation에만 ad queue 결과 emit.

직접 호출: `ProtocolError`, `float`, `read_decision`, `request.get`, `result.update`, `self.auth.request_json`, `self.emit`, `self.fetch_png`, `self.last_requested.get`, `str`, `time.monotonic`.

## `AdGateway.fetch_png(self, path)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |
| path | 없음 | 공개HTTP경로/신뢰된PNG경로. |

반환·실패: async bytes 또는ValueError/network 예외.

의사코드: 비어 있지 않은 CREATIVE_PATHS 원소 검사 → 같은 게임 origin GET(redirect 금지, timeout=3초) → status=200/MIME=image/png/크기/PNG header/차원 검사 → bytes 반환.

직접 호출: `ValueError`, `aiohttp.ClientTimeout`, `b''.join`, `chunks.append`, `isinstance`, `len`, `response.content.iter_chunked`, `self.auth.session.get`, `struct.unpack`.

## `AdGateway.start_event(self, request)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |
| request | 없음 | 기존 dict queue선택/사건요청. |

반환·실패: bool.

의사코드: slot/type/동일task 진행 검사 → async fetch_event task 소유.

직접 호출: `asyncio.create_task`, `dict`, `isinstance`, `request.get`, `self.fetch_event`, `self.tasks[key].done`.

## `AdGateway.fetch_event(self, request)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |
| request | 없음 | 기존 dict queue선택/사건요청. |

반환·실패: async None; 공개 queue 이벤트.

의사코드: generation/identity snapshot → 현재 Player/입력 → AuthSession.post_ad_event → 공개 성공·임시/영구 오류 → 현재generation에만 emit.

직접 호출: `ProtocolError`, `ValueError`, `isinstance`, `read_ad_event`, `request.get`, `result.update`, `self.auth.post_ad_event`, `self.emit`, `self.last_requested.pop`, `str`.

## `AdGateway.close(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |

반환·실패: async None.

의사코드: generation증가/identity해제 → tasks cancel/gather → owned상태 clear.

직접 호출: `asyncio.gather`, `self.last_requested.clear`, `self.tasks.clear`, `self.tasks.values`, `task.cancel`, `task.done`.

## 상태·값 출처

지역 변수는 입력·기존 설정·검증한 공개응답·monotonic시간 또는 자기fixture에서 얻으며 해당함수/클래스가 쓴다. 전역/타이머/큐/fixture의 주요 초기값과 쓰기 소유자는 위 파일설명에 기록한다. 실제env값·계정암호·cookie·CSRF토큰은기록하지않는다.
