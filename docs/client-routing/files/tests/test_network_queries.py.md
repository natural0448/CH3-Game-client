# tests/test_network_queries.py

## 책임

같은 HTTP session, redirect/HTML 차단과 버튼형 전체·행동·Kafka 수집 통계 GET을 검사한다.

## 메서드

`FakeAuth.__init__(self, response)` — Session과 같은 session을 쓰는 JsonHttpClient를 만든다.

`FakeAuth.request_json(self, method, path, *, payload=None, csrf=False)` — fake JsonHttpClient에 전달한다.

`JsonHttpTests.test_redirect_and_html_are_not_read_as_json(self)` — 302/401/HTML body가 JSON으로 읽히지 않고 로그인 문구가 나오는지 검사한다.

`analytics_summary(**changes)` — source·선택 원천 행 수·고유 사실·행동/방 배열과 제거 대상 필드를 포함한 전체 통계 응답을 만든다.

`QueryGatewayTests.test_analytics_get_uses_same_session_and_safe_allowlist(self)` — `/api/analytics/`가 기존 session, redirect=false, timeout을 사용하고 source·record_count만 허용하며 알 수 없는 필드를 queue 결과에서 제외하는지 검사한다.

`QueryGatewayTests.test_actions_get_uses_same_session_and_safe_queue(self)` — 명시 fetch 전 호출이 없고 GET path, redirect=false, timeout, safe event가 맞는지 검사한다.

`QueryGatewayTests.test_unavailable_and_login_response_are_not_zero(self)` — available=false가 미생성 문구이며 401/HTML이 0건·비밀값으로 보이지 않는지 검사한다.

`QueryGatewayTests.test_ingest_get_uses_same_session_and_maps_missing_and_errors(self)` — 명시 호출 전 요청이 없고 `/api/analytics/ingest/`의 redirect/timeout 정책, 허용 count, 미생성 무숫자 상태, 503·401 문구를 검사한다.

직접 호출: `JsonHttpClient`, `QueryGateway`, `Identity`, tests support fake.
