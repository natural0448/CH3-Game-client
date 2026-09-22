# tests/test_windows_feature.py

## 책임

시간 창 응답 허용 목록, 같은 인증 세션의 GET, 메인 스레드 패널과 로컬 필터를 회귀 검사한다.

## 함수·fixture

`window_summary() -> dict` — tumbling/sliding 여섯 행과 제거되어야 할 알 수 없는 필드가 포함된 API fixture를 반환한다.

`FakeAuth.__init__(self, response)` — 테스트 HTTP 응답을 기존 세션과 `JsonHttpClient`에 연결한다.

`FakeAuth.request_json(self, method, path, *, payload=None, csrf=False)` — 테스트용 기존 `JsonHttpClient`와 같은 `Session`으로 요청한다.

`Recorder.__init__(self)` — Pygame Surface·font·Layout과 빈 label 배열을 만든다.

`Recorder.text(self, value, *args, **kwargs)` — 그려진 일반 문자열을 기록한다.

`Recorder.wrapped(self, value, *args, **kwargs)` — 그려진 줄바꿈 문자열을 기록한다.

`Recorder.card(self, *args, **kwargs)` — 카드 호출을 허용하되 픽셀 검사는 하지 않는다.

`Recorder.button(self, name, label, enabled=True)` — 버튼 label을 기록한다.

## 테스트 클래스

- `WindowsGatewayTests.test_get_uses_existing_session_and_safe_allowlist(self)` — 경로, redirect 금지, timeout, 알 수 없는 필드 제거를 검사한다.
- `WindowsGatewayTests.test_unavailable_is_not_presented_as_zero(self)` — 미생성 응답에 숫자가 생기지 않는지 검사한다.
- `WindowsUiTests.setUpClass(cls)` — Pygame dummy display와 font를 초기화한다.
- `WindowsUiTests.tearDownClass(cls)` — Pygame을 종료한다.
- `WindowsUiTests.test_panel_shows_five_recent_rows_and_filters_without_request(self)` — 최근 5행과 로컬 tumbling 필터가 request 상태를 만들지 않는지 검사한다.
- `WindowsUiTests.test_empty_states_and_filter_hit_are_distinct(self)` — 미생성/빈 게시 결과 문구와 resize 좌표의 filter intent를 검사한다.

직접 호출: `read_windows`, `QueryGateway`, `QueryStore`, `draw_windows`, `InputRouter`, Pygame dummy display.
