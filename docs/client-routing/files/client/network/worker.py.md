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
