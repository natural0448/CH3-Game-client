# tests/test_ads_events.py

실제 class/function을 사용하는 상태·SDL dummy·network 회귀검사다. 표시 전 사건 없음, 노출 저장 뒤 클릭, 재전송False 성공, 상관관계/로그아웃,decode실패,hidden/minimized,400/403/404 중지와2초 새 선택,503 클릭 재시도,로비 사건 없음,공개 오류 allowlist를 검증한다. fake HTTP/합성 PNG/메모리 상태를 사용하며 실수업 데이터를 읽거나 쓰지 않는다.

직접 호출 기대 계약: UI/상태 helper는 각 짝 문서의 반환 계약을 따른다. worker.submit은접수bool, HTTP/JSON helper는공개dict 또는공개오류, read_ad_event는id/type/created dict, emit은queue전달, create_task는Task, Pygame draw/decode는Surface/표시receipt, fixture Web은bytes이다. 하위 계층 내부를 복제하지 않는다.

## `ready_controller()`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| 없음 | — | 인자없음 |

반환·실패: 준비된 Controller.

의사코드: 합성 Player/connected/선택성공을설정.

직접 호출: `Controller`, `NetworkStub`, `controller.game.apply_identity`, `controller.game.apply_state`, `controller.game.apply_status`, `controller.handle_network_event`, `controller.request_ad`, `decision`, `player`, `png`.

## `confirmation(request, created=False)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| request | 없음 | 기존 dict queue선택/사건요청. |
| created | False | 합성receipt의created bool. |

반환·실패: dict.

의사코드: 공개request에 synthetic성공 receipt/status를더함.

직접 호출: .

## `class EventStateTests(unittest.TestCase)`

기반클래스: unittest.TestCase; 필드 초기값/소유자는파일설명과메서드에서정한다.

## `EventStateTests.test_permanent_refusal_stops_events_and_allows_new_selection_after_two_seconds(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |

반환·실패: None; 불일치AssertionError.

의사코드: 테스트이름의 합성fixture → 실제클래스/함수 호출 → 상태/큐/receipt/오류 불변식 검증.

직접 호출: `controller.confirm_ad_display`, `decision`, `ready_controller`, `self.assertFalse`, `self.assertIsNone`, `self.assertIsNotNone`, `self.assertTrue`, `self.subTest`, `slot.accept_event`, `slot.request`, `slot.request_event`.

## `EventStateTests.test_click_timeout_retries_same_decision_after_another_visible_frame(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |

반환·실패: None; 불일치AssertionError.

의사코드: 테스트이름의 합성fixture → 실제클래스/함수 호출 → 상태/큐/receipt/오류 불변식 검증.

직접 호출: `confirmation`, `controller.confirm_ad_display`, `controller.request_ad_event`, `decision`, `len`, `ready_controller`, `self.assertEqual`, `self.assertIsNone`, `slot.accept_event`, `slot.request`.

## `EventStateTests.test_lobby_is_displayed_without_sending_classroom_events(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |

반환·실패: None; 불일치AssertionError.

의사코드: 테스트이름의 합성fixture → 실제클래스/함수 호출 → 상태/큐/receipt/오류 불변식 검증.

직접 호출: `controller.confirm_ad_display`, `controller.handle_network_event`, `controller.request_ad`, `controller.request_ad_event`, `decision`, `len`, `png`, `ready_controller`, `self.assertEqual`, `self.assertFalse`, `self.assertTrue`.

## `EventStateTests.test_decode_failure_allows_a_fresh_selection_without_an_event(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |

반환·실패: None; 불일치AssertionError.

의사코드: 테스트이름의 합성fixture → 실제클래스/함수 호출 → 상태/큐/receipt/오류 불변식 검증.

직접 호출: `controller.confirm_ad_display`, `decision`, `ready_controller`, `self.assertFalse`, `self.assertIsNone`, `self.assertIsNotNone`, `self.assertTrue`, `slot.request`.

## `EventStateTests.test_no_request_before_display_then_one_confirmed_impression_and_click(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |

반환·실패: None; 불일치AssertionError.

의사코드: 테스트이름의 합성fixture → 실제클래스/함수 호출 → 상태/큐/receipt/오류 불변식 검증.

직접 호출: `confirmation`, `controller.confirm_ad_display`, `controller.handle_network_event`, `controller.request_ad_event`, `decision`, `len`, `ready_controller`, `self.assertEqual`, `self.assertFalse`, `self.assertIsNone`, `self.assertTrue`, `slot.request`.

## `EventStateTests.test_retry_queue_failure_stale_ids_and_new_ad_reset(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |

반환·실패: None; 불일치AssertionError.

의사코드: 테스트이름의 합성fixture → 실제클래스/함수 호출 → 상태/큐/receipt/오류 불변식 검증.

직접 호출: `confirmation`, `controller.request_ad_event`, `ready_controller`, `self.assertEqual`, `self.assertFalse`, `self.assertIsNone`, `self.assertTrue`, `slot.accept_event`, `slot.request`, `slot.request_event`.

## `EventStateTests.test_event_contract_rejects_unsafe_confirmation(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |

반환·실패: None; 불일치AssertionError.

의사코드: 테스트이름의 합성fixture → 실제클래스/함수 호출 → 상태/큐/receipt/오류 불변식 검증.

직접 호출: `read_ad_event`, `self.assertEqual`, `self.assertRaises`.

## `EventStateTests.test_only_current_authentication_failure_clears_ad_and_logs_out(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |

반환·실패: None; 불일치AssertionError.

의사코드: 테스트이름의 합성fixture → 실제클래스/함수 호출 → 상태/큐/receipt/오류 불변식 검증.

직접 호출: `all`, `controller.ads.slots.values`, `controller.confirm_ad_display`, `controller.handle_network_event`, `decision`, `ready_controller`, `self.assertEqual`, `self.assertIsNone`, `self.assertTrue`.

## `class EventUiTests(unittest.TestCase)`

기반클래스: unittest.TestCase; 필드 초기값/소유자는파일설명과메서드에서정한다.

## `EventUiTests.setUpClass(cls)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| cls | 없음 | 해당테스트클래스/SDL fixture 소유자. |

반환·실패: None; 테스트실패AssertionError.

의사코드: 함수이름의 owned상태/fixture 준비 → 직접호출 → 공개결과 적용 또는불변식assert → 자기fixture 정리.

직접 호출: `pygame.display.init`, `pygame.display.set_mode`, `pygame.font.init`.

Decorator: `classmethod`.

## `EventUiTests.tearDownClass(cls)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| cls | 없음 | 해당테스트클래스/SDL fixture 소유자. |

반환·실패: None; 테스트실패AssertionError.

의사코드: 함수이름의 owned상태/fixture 준비 → 직접호출 → 공개결과 적용 또는불변식assert → 자기fixture 정리.

직접 호출: `pygame.quit`.

Decorator: `classmethod`.

## `EventUiTests.test_image_failure_hidden_panel_and_minimized_have_no_receipts(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |

반환·실패: None; 불일치AssertionError.

의사코드: 테스트이름의 합성fixture → 실제클래스/함수 호출 → 상태/큐/receipt/오류 불변식 검증.

직접 호출: `InputRouter`, `InputRouter().route`, `ScreenRenderer`, `build_layout`, `controller.screen_model`, `load_config`, `patch`, `png`, `pygame.display.get_surface`, `pygame.event.Event`, `ready_controller`, `renderer.render`, `self.assertEqual`, `self.assertIn`, `self.assertNotEqual`.

## `class EventNetworkTests(unittest.IsolatedAsyncioTestCase)`

기반클래스: unittest.IsolatedAsyncioTestCase; 필드 초기값/소유자는파일설명과메서드에서정한다.

## `EventNetworkTests.test_auth_session_distinguishes_permanent_rejection_and_transient_failure(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |

반환·실패: None; 불일치AssertionError.

의사코드: 테스트이름의 합성fixture → 실제클래스/함수 호출 → 상태/큐/receipt/오류 불변식 검증.

직접 호출: `AuthSession`, `auth.post_ad_event`, `getattr`, `load_config`, `self.assertEqual`, `self.assertRaises`, `self.subTest`.

## `EventNetworkTests.test_http_error_body_exposes_only_known_public_reasons(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |

반환·실패: None; 불일치AssertionError.

의사코드: 테스트이름의 합성fixture → 실제클래스/함수 호출 → 상태/큐/receipt/오류 불변식 검증.

직접 호출: `Content`, `JsonHttpClient`, `Response`, `SimpleNamespace`, `http.request_json`, `self.assertEqual`, `self.assertNotIn`, `self.assertRaises`, `self.subTest`, `str`.

## `EventNetworkTests.test_gateway_permanent_refusal_clears_selection_cooldown(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |

반환·실패: None; 불일치AssertionError.

의사코드: 테스트이름의 합성fixture → 실제클래스/함수 호출 → 상태/큐/receipt/오류 불변식 검증.

직접 호출: `AdGateway`, `SimpleNamespace`, `events.append`, `gateway.close`, `gateway.fetch_event`, `gateway.set_identity`, `self.assertNotIn`, `self.assertTrue`.

## `EventNetworkTests.test_current_session_csrf_and_public_duplicate_receipt(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |

반환·실패: None; 불일치AssertionError.

의사코드: 테스트이름의 합성fixture → 실제클래스/함수 호출 → 상태/큐/receipt/오류 불변식 검증.

직접 호출: `AdGateway`, `AuthSession`, `SimpleNamespace`, `events.append`, `gateway.close`, `gateway.fetch_event`, `gateway.set_identity`, `load_config`, `self.assertEqual`, `self.assertFalse`.

## `EventNetworkTests.test_event_401_uses_lesson_error_result_and_login_flag(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |

반환·실패: None; 불일치AssertionError.

의사코드: 테스트이름의 합성fixture → 실제클래스/함수 호출 → 상태/큐/receipt/오류 불변식 검증.

직접 호출: `AdGateway`, `SimpleNamespace`, `events.append`, `gateway.close`, `gateway.fetch_event`, `gateway.set_identity`, `self.assertEqual`, `self.assertTrue`.

## `EventNetworkTests.test_busy_worker_returns_correlated_error_instead_of_dropping_request(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |

반환·실패: None; 불일치AssertionError.

의사코드: 테스트이름의 합성fixture → 실제클래스/함수 호출 → 상태/큐/receipt/오류 불변식 검증.

직접 호출: `NetworkWorker`, `asyncio.create_task`, `asyncio.sleep`, `patch`, `range`, `self.assertEqual`, `self.assertIsNone`, `worker._run`, `worker._stop.set`, `worker.events.empty`, `worker.events.get_nowait`, `worker.submit`.

## 상태·값 출처

지역 변수는 입력·기존 설정·검증한 공개응답·monotonic시간 또는 자기fixture에서 얻으며 해당함수/클래스가 쓴다. 전역/타이머/큐/fixture의 주요 초기값과 쓰기 소유자는 위 파일설명에 기록한다. 실제env값·계정암호·cookie·CSRF토큰은기록하지않는다.

## 내부 fixture helper

- `EventNetworkTests.test_http_error_body_exposes_only_known_public_reasons.Content.read(self, size)`: 해당테스트의입력·가짜응답/task를 준비/반환한다. 외부서버/실수업DB를호출하지않고 enclosing테스트가수명/결과를소유한다.
- `EventNetworkTests.test_http_error_body_exposes_only_known_public_reasons.Response.__aenter__(self)`: 해당테스트의입력·가짜응답/task를 준비/반환한다. 외부서버/실수업DB를호출하지않고 enclosing테스트가수명/결과를소유한다.
- `EventNetworkTests.test_http_error_body_exposes_only_known_public_reasons.Response.__aexit__(self, *args)`: 해당테스트의입력·가짜응답/task를 준비/반환한다. 외부서버/실수업DB를호출하지않고 enclosing테스트가수명/결과를소유한다.
- `EventNetworkTests.test_gateway_permanent_refusal_clears_selection_cooldown.post_ad_event(*args)`: 해당테스트의입력·가짜응답/task를 준비/반환한다. 외부서버/실수업DB를호출하지않고 enclosing테스트가수명/결과를소유한다.
- `EventNetworkTests.test_current_session_csrf_and_public_duplicate_receipt.refresh_csrf()`: 해당테스트의입력·가짜응답/task를 준비/반환한다. 외부서버/실수업DB를호출하지않고 enclosing테스트가수명/결과를소유한다.
- `EventNetworkTests.test_current_session_csrf_and_public_duplicate_receipt.request_json(method, path, **kwargs)`: 해당테스트의입력·가짜응답/task를 준비/반환한다. 외부서버/실수업DB를호출하지않고 enclosing테스트가수명/결과를소유한다.
- `EventNetworkTests.test_event_401_uses_lesson_error_result_and_login_flag.post_ad_event(decision_id, event_type)`: 해당테스트의입력·가짜응답/task를 준비/반환한다. 외부서버/실수업DB를호출하지않고 enclosing테스트가수명/결과를소유한다.
- `EventNetworkTests.test_busy_worker_returns_correlated_error_instead_of_dropping_request.Component.__init__(self, *args)`: 해당테스트의입력·가짜응답/task를 준비/반환한다. 외부서버/실수업DB를호출하지않고 enclosing테스트가수명/결과를소유한다.
- `EventNetworkTests.test_busy_worker_returns_correlated_error_instead_of_dropping_request.Component.close(self)`: 해당테스트의입력·가짜응답/task를 준비/반환한다. 외부서버/실수업DB를호출하지않고 enclosing테스트가수명/결과를소유한다.
- `EventNetworkTests.test_busy_worker_returns_correlated_error_instead_of_dropping_request.Component.check_timeout(self)`: 해당테스트의입력·가짜응답/task를 준비/반환한다. 외부서버/실수업DB를호출하지않고 enclosing테스트가수명/결과를소유한다.
- `EventNetworkTests.test_busy_worker_returns_correlated_error_instead_of_dropping_request.Component.start_event(self, request)`: 해당테스트의입력·가짜응답/task를 준비/반환한다. 외부서버/실수업DB를호출하지않고 enclosing테스트가수명/결과를소유한다.
