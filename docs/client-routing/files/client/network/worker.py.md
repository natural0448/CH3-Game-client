# client/network/worker.py

## 책임과 상태

thread 한 개, asyncio loop 한 개, request/result queue와 task 종료 순서만 조정한다. `QUERY_KINDS=frozenset(QUERY_SPECS)`로 읽기 계약의 delivery/analytics/actions/ingest/windows/load/metrics/history 집합을 그대로 사용한다.

## 메서드

`NetworkWorker.__init__(self, config)` — AuthSession과 command timeout, bounded request queue, event queue, 단일 thread를 준비한다.

`NetworkWorker.start(self)` — worker thread를 한 번만 시작한다.

`NetworkWorker.submit(self, request)` — dict 복사본을 nonblocking queue에 넣고 성공 여부를 반환한다.

`NetworkWorker.drain_events(self, limit=200)` — 메인 스레드가 최대 limit개의 event를 가져간다.

`NetworkWorker.is_alive(self)` — thread 생존 여부를 반환한다.

`NetworkWorker.stop(self, timeout=None)` — stop flag와 main task cancel을 전달하고 선택적으로 join한다.

`NetworkWorker._emit(self, kind, **data)` — credential-free event dict를 result queue에 넣는다.

`NetworkWorker._thread_main(self)` — `asyncio.run(_run)` 후 stopped를 emit하며 예외 repr를 노출하지 않는다.

`NetworkWorker._run(self)`

```text
같은 loop에 PlayChannel과 QueryGateway 생성
고정 dispatch: login/logout/command 또는 QUERY_SPECS에 등록된 query kind
PlayChannel timeout 확인
처리 후 request.clear로 password 참조 제거
finally query → play → session 순으로 닫고 queue 비움
```

`NetworkWorker._login(self, request)` — 기존 구성 정리 → AuthSession.login → Identity emit → Query identity와 Play task 설정.

`NetworkWorker._logout(self)` — query generation 차단 → WS 닫기 → 최신 CSRF logout POST → query/session 닫기 → local logged_out event.

직접 호출: `AuthSession`, `PlayChannel`, `QueryGateway`, `asyncio`, `queue`, `threading`.

## 22일차 이미지 광고 최종 반영

NetworkWorker는 기존 하나의 thread/loop/AuthSession 위에 AdGateway를 구성한다. ad 요청은 start로 별도 async task, busy는 correlated error event. 로그인 성공 identity 전달, 계정 변경/로그아웃/종료에서 gateway close. 이미지 URL은 게임 origin만 접속한다. Pygame import를 추가하지 않는다. 기존 WS/action/query routing은 유지한다.

클래스 계약: `class NetworkWorker`.


### `NetworkWorker.__init__(self, config)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |
| config | 없음 | load_config의 공개 설정 dict; 계정/매체키 없음. |

반환·실패: None.

의사코드: 해당 파일 책임에 정의한 소유 상태/fixture를 초기화·정리 또는 교체.

직접 호출: `AuthSession`, `float`, `queue.Queue`, `threading.Thread`, `threading.Event`, `config.get`, `ValueError`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `NetworkWorker.start(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |

반환·실패: None.

의사코드: 기존 입력·상태 검사 → 직접 호출 → 현재 결과/상태 전달; 이미지 추가 책임은 위 파일 설명 참조.

직접 호출: `self.thread.start`, `RuntimeError`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `NetworkWorker.submit(self, request)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |
| request | 없음 | 해당 계층의 Django HttpRequest 또는 public correlated queue dict. |

반환·실패: 코드 반환 식: `False`, `True`.

의사코드: 기존 입력·상태 검사 → 직접 호출 → 현재 결과/상태 전달; 이미지 추가 책임은 위 파일 설명 참조.

직접 호출: `self._stop.is_set`, `self.requests.put_nowait`, `dict`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `NetworkWorker.drain_events(self, limit=200)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |
| limit | `200` | 기존 limit 입력; 아래 동작·직접 호출과 기존 계약 참조. |

반환·실패: 코드 반환 식: `result`.

의사코드: 기존 입력·상태 검사 → 직접 호출 → 현재 결과/상태 전달; 이미지 추가 책임은 위 파일 설명 참조.

직접 호출: `range`, `max`, `result.append`, `self.events.get_nowait`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `NetworkWorker.is_alive(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |

반환·실패: 코드 반환 식: `self.thread.is_alive()`.

의사코드: 기존 입력·상태 검사 → 직접 호출 → 현재 결과/상태 전달; 이미지 추가 책임은 위 파일 설명 참조.

직접 호출: `self.thread.is_alive`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `NetworkWorker.stop(self, timeout=None)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |
| timeout | `None` | 기존 timeout 입력; 아래 동작·직접 호출과 기존 계약 참조. |

반환·실패: None.

의사코드: 기존 입력·상태 검사 → 직접 호출 → 현재 결과/상태 전달; 이미지 추가 책임은 위 파일 설명 참조.

직접 호출: `self._stop.set`, `self.thread.join`, `self.loop.is_closed`, `self.loop.call_soon_threadsafe`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `NetworkWorker._emit(self, kind, **data)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |
| kind | 없음 | 기존 kind 입력; 아래 동작·직접 호출과 기존 계약 참조. |
| data | 없음 | 요청/조회 public dict 또는 Django POST mapping; 파일 책임의 필드·타입 범위 참조. |

반환·실패: None.

의사코드: 기존 입력·상태 검사 → 직접 호출 → 현재 결과/상태 전달; 이미지 추가 책임은 위 파일 설명 참조.

직접 호출: `self.events.put`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `NetworkWorker._thread_main(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |

반환·실패: None.

의사코드: 기존 입력·상태 검사 → 직접 호출 → 현재 결과/상태 전달; 이미지 추가 책임은 위 파일 설명 참조.

직접 호출: `asyncio.run`, `self._emit`, `self._run`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `NetworkWorker._run(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |

반환·실패: None.

의사코드: 기존 입력·상태 검사 → 직접 호출 → 현재 결과/상태 전달; 이미지 추가 책임은 위 파일 설명 참조.

직접 호출: `asyncio.get_running_loop`, `asyncio.current_task`, `PlayChannel`, `QueryGateway`, `AdGateway`, `self._stop.is_set`, `self.ads.close`, `self.queries.close`, `self.play.close`, `self.auth.close`, `self.play.check_timeout`, `self.requests.get_nowait`, `request.get`, `request.clear`, `self.requests.get_nowait().clear`, `self._emit`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `NetworkWorker._login(self, request)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |
| request | 없음 | 해당 계층의 Django HttpRequest 또는 public correlated queue dict. |

반환·실패: None.

의사코드: 기존 입력·상태 검사 → 직접 호출 → 현재 결과/상태 전달; 이미지 추가 책임은 위 파일 설명 참조.

직접 호출: `self._emit`, `request.pop`, `self.ads.close`, `self.queries.close`, `self.play.close`, `self.auth.close`, `self.queries.set_identity`, `self.ads.set_identity`, `self.play.start`, `self.auth.login`, `str`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `NetworkWorker._logout(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |

반환·실패: None.

의사코드: 기존 입력·상태 검사 → 직접 호출 → 현재 결과/상태 전달; 이미지 추가 책임은 위 파일 설명 참조.

직접 호출: `self._emit`, `self.queries.invalidate`, `self.ads.close`, `self.play.close`, `self.auth.logout`, `self.queries.close`, `self.auth.close`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.
