# client/network/ads.py

worker asyncio loop의 AdGateway. auth는 기존 AuthSession, emit은 queue 결과 sink, identity는 공개 로그인 Player 정보, generation은 계정 경계다. tasks는 슬롯 선택 및 (slot,event_type) task를 소유하며 close에서 cancel/gather/clear한다. last_requested는 슬롯별 monotonic15초 제한이다. 현재 generation의 영구 사건 거절에는 해당 선택 cooldown을 제거해 상태 계층의2초 새 선택 정책을 허용한다. 성공 result는 공개 decision/PNG 또는 id/type/created receipt만 담는다. 영구400/403/404(302/401은 재로그인)는 event_rejected=True, needs_login은302/401이다. 임시 장애/시간초과는 같은 결정을 재시도한다. PNG는 기존 동일 origin whitelist·1MiB/1024차원 상한이다.

직접 호출 기대 계약: UI/상태 helper는 각 짝 문서의 반환 계약을 따른다. worker.submit은접수bool, HTTP/JSON helper는공개dict 또는공개오류, read_ad_event는id/type/created dict, emit은queue전달, create_task는Task, Pygame draw/decode는Surface/표시receipt, fixture Web은bytes이다. 하위 계층 내부를 복제하지 않는다.

## `class AdGateway`

기반클래스: ; 필드 초기값/소유자는파일설명과메서드에서정한다.

## `AdGateway.__init__(self, auth_session, emit)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |
| auth_session | 없음 | worker가소유한 AuthSession. |
| emit | 없음 | 공개queue event sink callable. |

반환·실패: None.

의사코드: 기존생성자입력에서owned상태/멤버 초기화.

직접 호출: .

## `AdGateway.set_identity(self, identity)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |
| identity | 없음 | 현재공개게임 Identity. |

반환·실패: None.

의사코드: 현재identity 대입 → generation증가.

직접 호출: .

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

의사코드: identity/15초 → CSRF선택 POST → public contract/필요PNG → 현재generation emit.

직접 호출: `ProtocolError`, `float`, `read_decision`, `request.get`, `result.update`, `self.auth.request_json`, `self.emit`, `self.fetch_png`, `self.last_requested.get`, `str`, `time.monotonic`.

## `AdGateway.fetch_png(self, path)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |
| path | 없음 | 공개HTTP경로/신뢰된PNG경로. |

반환·실패: async bytes 또는ValueError/network 예외.

의사코드: whitelist/같은게임origin GET → status/MIME/size/header/dimensions 검사.

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
