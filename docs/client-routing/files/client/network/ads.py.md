# client/network/ads.py

## 22일차 이미지 광고 최종 반영

AdGateway 초기 identity=None/generation=0/tasks·last_requested={}다. 기존 AuthSession/session을 재사용하며 새 키·비밀번호를 소유하지 않는다. 슬롯당 하나의 task,15초 제한, POST session/CSRF, 공개 계약 검사 후 게임-origin PNG만 읽는다. redirect 금지, timeout3s, image/png,1MiB·가로세로1..1024, PNG signature 제한. decode는 하지 않고 bytes를 보낸다. close는 generation 증가·task cancel·기록 clear로 계정 변경 후 늦은 응답을 차단한다.

클래스 계약: `class AdGateway`.


### `AdGateway.__init__(self, auth_session, emit)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |
| auth_session | 없음 | 기존 인증 세션; 소유한 ClientSession/session/CSRF 요청을 재사용. |
| emit | 없음 | 기존 worker의 public result queue callback(kind,**data). |

반환·실패: None.

의사코드: 해당 파일 책임에 정의한 소유 상태/fixture를 초기화·정리 또는 교체.

직접 호출: 없음. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `AdGateway.set_identity(self, identity)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |
| identity | 없음 | 성공 로그인 Identity 또는 None. |

반환·실패: None.

의사코드: 해당 파일 책임에 정의한 소유 상태/fixture를 초기화·정리 또는 교체.

직접 호출: 없음. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `AdGateway.start(self, request)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |
| request | 없음 | 해당 계층의 Django HttpRequest 또는 public correlated queue dict. |

반환·실패: task 접수 bool.

의사코드: 허용 slot과 기존 진행 task 검사 → async fetch task 소유.

직접 호출: `request.get`, `asyncio.create_task`, `self.fetch`, `isinstance`, `dict`, `self.tasks[slot].done`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `AdGateway.fetch(self, request)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |
| request | 없음 | 해당 계층의 Django HttpRequest 또는 public correlated queue dict. |

반환·실패: async None; 오류는 공개 error event.

의사코드: generation/identity snapshot → 계정·cooldown → CSRF POST → public contract → 필요PNG bytes → 현재 generation에만 emit.

직접 호출: `request.get`, `time.monotonic`, `read_decision`, `result.update`, `self.emit`, `ProtocolError`, `self.auth.request_json`, `self.last_requested.get`, `self.fetch_png`, `float`, `str`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `AdGateway.fetch_png(self, path)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |
| path | 없음 | 허용된 상대 PNG URL 또는 fixture HTTP 경로; 외부 URL은 PNG fetch 금지. |

반환·실패: async PNG bytes; 실패 ValueError 또는 network 오류.

의사코드: whitelist path → 동일게임origin GET → redirect/MIME/크기/헤더/차원 검사.

직접 호출: `ValueError`, `self.auth.session.get`, `response.content.iter_chunked`, `b''.join`, `struct.unpack`, `isinstance`, `len`, `chunks.append`, `aiohttp.ClientTimeout`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `AdGateway.close(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |

반환·실패: async None.

의사코드: generation 증가 → identity None → running task cancel/gather → 슬롯 task/cooldown clear.

직접 호출: `self.tasks.clear`, `self.last_requested.clear`, `task.cancel`, `self.tasks.values`, `asyncio.gather`, `task.done`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.
