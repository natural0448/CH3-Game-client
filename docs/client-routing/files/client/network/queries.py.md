# client/network/queries.py

## 책임과 상태

버튼으로 요청된 읽기 전용 GET을 같은 AuthSession에서 실행한다. `tasks`는 kind별 최대 하나, `generation`은 늦은 계정 응답 차단, `last_requested_at`은 worker 측 최소 간격 방어다.

## 메서드

`QueryGateway.__init__(self, auth_session, emit)` — 같은 session facade와 결과 queue callback을 저장한다.

`QueryGateway.set_identity(self, identity)` — 현재 공개 Identity를 설정하고 generation을 올린다.

`QueryGateway.invalidate(self)` — identity를 비워 늦은 결과를 막는다.

`QueryGateway.start(self, request)` — `QUERY_SPECS` 허용 kind와 중복 task를 검사하고 `fetch` task를 만든다.

`QueryGateway.fetch(self, request)`

```text
player_id와 최소 간격 확인
AuthSession.request_json('GET', 고정 spec.path)
history 또는 spec.parser로 허용 필드만 생성
available=false를 empty_message로 유지
request_id/player_id/path/status/json/message를 emit
302/401 ProtocolError는 로그인 안내, HTML은 parser에 전달하지 않음
```

`QueryGateway.close(self)` — generation 무효화, 모든 조회 task cancel/gather, 간격 상태 초기화.

직접 호출: `QUERY_SPECS`, `AuthSession.request_json`, `asyncio.create_task/gather`, `time.monotonic`.
