# tests/test_network_queries.py

## 책임

같은 HTTP session, redirect/HTML 차단과 버튼형 행동 통계 GET을 검사한다.

## 메서드

`FakeAuth.__init__(self, response)` — Session과 같은 session을 쓰는 JsonHttpClient를 만든다.

`FakeAuth.request_json(self, method, path, *, payload=None, csrf=False)` — fake JsonHttpClient에 전달한다.

`JsonHttpTests.test_redirect_and_html_are_not_read_as_json(self)` — 302/401/HTML body가 JSON으로 읽히지 않고 로그인 문구가 나오는지 검사한다.

`QueryGatewayTests.test_actions_get_uses_same_session_and_safe_queue(self)` — 명시 fetch 전 호출이 없고 GET path, redirect=false, timeout, safe event가 맞는지 검사한다.

`QueryGatewayTests.test_unavailable_and_login_response_are_not_zero(self)` — available=false가 미생성 문구이며 401/HTML이 0건·비밀값으로 보이지 않는지 검사한다.

직접 호출: `JsonHttpClient`, `QueryGateway`, `Identity`, tests support fake.
