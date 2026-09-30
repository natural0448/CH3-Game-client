# tests/test_lake_feature.py

## 책임·fixture·직접 의존성

원본 보존의 작은 응답 계약, 같은 세션의 버튼형 GET, 로그인/HTML/timeout 처리, IP 쿠키 제한, 패널과 API 응답 보기를 검증한다. 실제 서버·계정·Kafka·Spark에 연결하지 않는다. SDL_VIDEODRIVER는 dummy, PYGAME_HIDE_SUPPORT_PROMPT는 1로 기본 설정한다.

직접 호출: unittest와 Mock/AsyncMock, pygame 초기화·종료·Surface·event, yarl.URL, read_lake, QueryGateway, AuthSession, Controller, QueryStore, InputRouter, build_layout, draw_lake/draw_query_panels/draw_api/draw_activity. 기존 tests.support 및 test_network_queries.FakeAuth, test_day18_metrics.Recorder를 재사용한다.

`lake_response(**changes)` — changes는 필드 덮어쓰기 사전이다. schema_version=1/status=ready/dataset_version=capture-002/rows=5766/bytes=4590247, timezone 포함 테스트 시각, matched=True, verification_scope=local-and-copied-bytes인 새 fixture 사전을 반환한다. 실측 snapshot을 만드는 함수가 아니다.

## 계약 검사

`class LakeContractTests(unittest.TestCase)`

- `LakeContractTests.test_ready_copies_only_small_public_fields(self)` — fixture에 원본 배열·계정/인증 관련 여분 필드를 넣고 read_lake 결과에서 제거되는지 검사; None 반환.
- `LakeContractTests.test_pending_and_unavailable_do_not_invent_measurements(self)` — 준비/조회 불가에 숫자·matched가 없고 available=False인지 검사; None 반환.
- `LakeContractTests.test_invalid_verification_types_and_times_are_rejected(self)` — 잘못된 bool/int·상태·검사 범위·timezone 없는 시각의 ValueError 검사; None 반환.

## 비동기 통신 검사

`class LakeGatewayTests(unittest.IsolatedAsyncioTestCase)`

`LakeGatewayTests.fetch(self, response)` — response는 tests.support.Response다. 기존 FakeAuth와 결과 callback 목록을 조립하고 공개 Identity를 설정한 후 lake-id 요청을 fetch한다. `(auth, event)`를 반환한다.

- `LakeGatewayTests.test_get_uses_existing_session_policy_and_worker_registration(self)` — fetch 결과의 정확한 GET 주소·allow_redirects=False·timeout=8과 worker 허용 kind를 검사; None 반환.
- `LakeGatewayTests.test_redirect_unauthorized_and_html_are_login_guidance_without_body(self)` — 302/401/200 HTML에서 body 미읽기·로그인 안내·비밀 본문 미노출 검사; None 반환.
- `LakeGatewayTests.test_pending_unavailable_and_503_keep_distinct_messages(self)` — pending 준비 안내와 unavailable/503 조회 불가 안내를 구분; None 반환.
- `LakeGatewayTests.test_network_timeout_and_missing_login_do_not_emit_counts(self)` — Identity 없는 요청은 HTTP를 보내지 않고, timeout 결과는 숫자 없는 조회 불가인지 검사; None 반환.
- `LakeGatewayTests.test_ip_cookies_are_allowed_only_on_loopback_and_sessions_are_independent(self)` — 루프백 IPv4/IPv6·localhost와 원격 IP의 실제 cookie 보관 동작을 대조하고 두 계정 session의 격리·close를 검사; None 반환.

## 메인 스레드 UI·상관관계 검사

`class LakeUiTests(unittest.TestCase)`

- `LakeUiTests.setUpClass(cls)` — cls는 테스트 클래스. dummy display와 font 초기화; None 반환.
- `LakeUiTests.tearDownClass(cls)` — pygame.quit으로 테스트 자원 정리; None 반환.
- `LakeUiTests.test_ready_panel_displays_scope_times_and_match_both_ways(self)` — ready 응답을 정제해 Recorder에 그리고 두 시각·행/byte 단위·검사 범위·matched True/False 문구 검사; None 반환.
- `LakeUiTests.test_pending_and_unavailable_panels_have_no_fake_zero(self)` — 일반 패널 합성 경로에서 준비/조회 불가 문구와 숫자 미생성 검사; None 반환.
- `LakeUiTests.test_refresh_and_entry_hit_testing_survive_resize_with_ad_slots_preserved(self)` — 1100×880/800×640/320×240 좌표에서 entry/refresh가 lake query intent 하나로 변환되는지 검사. village-board/lobby-banner와 두 광고 Rect 유지 검사; None 반환.
- `LakeUiTests.test_single_queue_request_and_response_do_not_change_game_state(self)` — 같은 busy 요청의 중복 제출 차단, 일치 request_id 응답 처리, 게임 state 불변, API 보기의 lake 경로·라벨, 완료 후 재조회 검사; None 반환.

## 의사코드

```text
작은 공개 응답 fixture와 fake HTTP를 만든다
parser의 허용 목록·타입·시각·범위를 검증한다
gateway를 통해 로그인 상태별 GET과 결과 queue payload를 검증한다
실제 CookieJar의 쿠키 수락·격리·종료를 검증한다
dummy Pygame에서 패널·API 라벨과 resize 좌표의 intent를 검증한다
Controller의 query 처리 전후 GameState를 비교한다
```
