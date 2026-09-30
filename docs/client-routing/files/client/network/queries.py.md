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
ingest 503은 '마지막 수집 통계를 읽을 수 없음'으로 변환
lake의 pending은 준비 중, unavailable은 원본 보존 조회 불가로 표시
lake의 302/401 등 인증 오류는 기존 로그인 안내 유지
lake의 200 비JSON 응답은 본문을 읽지 않고 조회 불가·로그인 상태 안내
lake의 503 등 HTTP 실패·형식 오류·timeout은 조회 불가로 표시
```

`QueryGateway.close(self)` — generation 무효화, 모든 조회 task cancel/gather, 간격 상태 초기화.

직접 호출: `QUERY_SPECS`, `AuthSession.request_json`, `asyncio.create_task/gather`, `time.monotonic`.

lake도 tasks/generation/request_id/player_id 상관관계를 공유한다. json에는 parser가 허용한 작은 검사 snapshot만 넣는다. UI가 받는 공개 응답에서는 내부 상관관계 player_id를 표시하지 않는다. 새로운 session·thread·loop를 만들지 않는다.
