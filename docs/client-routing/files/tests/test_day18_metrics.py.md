# `tests/test_day18_metrics.py`

## 책임

18일차 부하 측정·운영 지표 응답이 기존 인증 session과 worker query 경로를 사용하고, 허용 필드만 메인 스레드 카드에 표시되는지 검사한다.

## fixture 함수

- `load_response()` — 50명 요청, 48명 연결과 방별 결과가 있는 `/api/analytics/load/` 예시.
- `metrics_response()` — DB count, 불완전 Kafka lag와 별도 Spark 시각이 있는 `/api/analytics/metrics/` 예시.

## 보조 클래스

- `FakeAuth.__init__(self, response)` — 기존 `JsonHttpClient`와 기록 가능한 fake session을 조립한다.
- `FakeAuth.request_json(self, method, path, *, payload=None, csrf=False)` — gateway 요청을 기존 JSON HTTP 정책에 전달한다.
- `Recorder.__init__(self)` — Pygame surface와 실제 Layout, font, label 목록을 준비한다.
- `Recorder.text(self, value, *args, **kwargs)` — 일반 텍스트 값을 수집한다.
- `Recorder.wrapped(self, value, *args, **kwargs)` — 줄바꿈 텍스트 값을 수집한다.
- `Recorder.card(self, *args, **kwargs)` — 테스트에서는 카드 배경 그리기를 생략한다.
- `Recorder.button(self, name, label, enabled=True)` — 버튼 라벨을 수집한다.

## 테스트 메서드 시그니처

- `Day18GatewayTests.test_gets_use_the_authenticated_session_and_allowlisted_json(self)`
- `Day18GatewayTests.test_unavailable_and_login_response_are_not_numbers(self)`
- `Day18UiTests.setUpClass(cls)`
- `Day18UiTests.tearDownClass(cls)`
- `Day18UiTests.test_load_card_keeps_units_and_room_scope(self)`
- `Day18UiTests.test_metrics_card_keeps_generated_and_spark_times_separate(self)`
- `Day18UiTests.test_refresh_controls_route_without_touching_game_state(self)`

## 테스트 흐름

```text
load/metrics가 같은 인증 session으로 redirect 없는 GET을 보내는지 확인
401 HTML 본문과 인증 정보가 결과 queue에 포함되지 않는지 확인
available=false가 0이 아닌 '아직 측정 전'으로 표시되는지 확인
부하 단위, 방별 실행 범위 안내와 동률 시 room_id가 앞선 최다 응답 방이 표시되는지 확인
metrics generated_at과 Spark timestamp가 별도 라벨인지 확인
resize 좌표 변환 후 refresh 클릭이 query intent만 만드는지 확인
```
