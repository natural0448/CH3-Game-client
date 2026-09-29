# tests/test_actions_ui.py

## 책임

메인 스레드 전체·행동·Kafka 수집 패널 문구, resize hit test, 로그인 focus와 전체 화면 render를 검사한다.

## Recorder 메서드

`Recorder.__init__(self)` — dummy canvas/font/Layout과 labels를 만든다.

`Recorder.text(self, value, *args, **kwargs)` — 표시 문자열을 기록한다.

`Recorder.wrapped(self, value, *args, **kwargs)` — 줄바꿈 표시 문자열을 기록한다.

`Recorder.card(self, *args, **kwargs)` — 카드 호출을 허용한다.

`Recorder.button(self, name, label, enabled=True)` — 버튼 label을 기록한다.

## 테스트 메서드

`ActionUiTests.setUpClass(cls)` — dummy SDL display와 font를 초기화한다.

`ActionUiTests.tearDownClass(cls)` — Pygame을 종료한다.

`ActionUiTests.test_available_and_unavailable_copy(self)` — source/time/고유 행동/원본 행/세 카드/방별/미생성 문구와 watermark 도움말을 검사한다.

`ActionUiTests.test_analytics_card_labels_optional_rows_and_refresh_hit(self)` — raw/delta 원천 이름, 고유 확정 사실, 선택적 원천 행 수, 집계 시각, 빈 그룹·미생성 표시와 analytics_refresh hit를 검사한다.

`ActionUiTests.test_same_layout_drives_resized_hit_and_login_focus_blocks_direction(self)` — 세 해상도 hit와 로그인 focus 중 방향키 차단을 검사한다.

`ActionUiTests.test_ingest_card_and_unavailable_copy(self)` — source, 세 count 단위, 행동 목록, Spark 미실행 안내, 미생성 무숫자 문구와 세 해상도 ingest_refresh hit를 검사한다.

`ActionUiTests.test_complete_screen_renders_from_read_only_model(self)` — ScreenModel로 800×640 전체 프레임을 그린다.

`ActionUiTests.test_complete_screen_renders_from_read_only_model.Port.submit(self, request)` — 화면 smoke test의 network port가 요청을 받아 True를 반환한다.

`ActionUiTests.test_complete_screen_renders_from_read_only_model.Port.stop(self, timeout=None)` — smoke test port의 side effect 없는 종료 메서드다.

직접 호출: `draw_actions`, `draw_ingest`, `InputRouter`, `Layout`, `ScreenRenderer`, `Controller`.
