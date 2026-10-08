# tests/test_ads_feature.py

기존 광고 선택/공개 필드/PNG/계정·UI 회귀검사. 유지 시간 테스트는 지연된 첫 표시를100초에 확인하고10초 보존/노출 저장 확인 후110초에만 다음 선택을 허용한다. NetworkStub은 queue test 대역이며 실제 서버를 호출하지 않는다. PNG는 합성 fixture다.

직접 호출 기대 계약: UI/상태 helper는 각 짝 문서의 반환 계약을 따른다. worker.submit은접수bool, HTTP/JSON helper는공개dict 또는공개오류, read_ad_event는id/type/created dict, emit은queue전달, create_task는Task, Pygame draw/decode는Surface/표시receipt, fixture Web은bytes이다. 하위 계층 내부를 복제하지 않는다.

## `png()`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| 없음 | — | 인자없음 |

반환·실패: bytes.

의사코드: 합성1×1 PNG bytes 구성.

직접 호출: `chunk`, `struct.pack`, `zlib.compress`.

## `decision()`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| 없음 | — | 인자없음 |

반환·실패: dict.

의사코드: 합성선택 fixture의 공개필드구성.

직접 호출: .

## `class NetworkStub`

기반클래스: ; 필드 초기값/소유자는파일설명과메서드에서정한다.

## `NetworkStub.__init__(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |

반환·실패: None.

의사코드: 기존생성자입력에서owned상태/멤버 초기화.

직접 호출: .

## `NetworkStub.submit(self, request)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |
| request | 없음 | 기존 dict queue선택/사건요청. |

반환·실패: True bool.

의사코드: 공개request를복사하여requests에append.

직접 호출: `dict`, `self.requests.append`.

## `class AdStateTests(unittest.TestCase)`

기반클래스: unittest.TestCase; 필드 초기값/소유자는파일설명과메서드에서정한다.

## `AdStateTests.test_retention_stale_identity_and_display_receipt(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |

반환·실패: None; 불일치AssertionError.

의사코드: 테스트이름의 합성fixture → 실제클래스/함수 호출 → 상태/큐/receipt/오류 불변식 검증.

직접 호출: `AdStore`, `decision`, `png`, `self.assertFalse`, `self.assertIsNone`, `self.assertIsNotNone`, `self.assertTrue`, `slot.accept`, `slot.accept_event`, `slot.request`, `slot.request_event`, `store.mark_displayed`, `store.reset`.

## `AdStateTests.test_public_contract_and_unsafe_values(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |

반환·실패: None; 불일치AssertionError.

의사코드: 테스트이름의 합성fixture → 실제클래스/함수 호출 → 상태/큐/receipt/오류 불변식 검증.

직접 호출: `decision`, `read_decision`, `self.assertIsNone`, `self.assertNotIn`, `self.assertRaises`, `self.subTest`.

## `class AdNetworkTests(unittest.IsolatedAsyncioTestCase)`

기반클래스: unittest.IsolatedAsyncioTestCase; 필드 초기값/소유자는파일설명과메서드에서정한다.

## `AdNetworkTests.test_existing_session_csrf_post_and_same_origin_png(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |

반환·실패: None; 불일치AssertionError.

의사코드: 테스트이름의 합성fixture → 실제클래스/함수 호출 → 상태/큐/receipt/오류 불변식 검증.

직접 호출: `AdGateway`, `Session`, `SimpleNamespace`, `events.append`, `gateway.close`, `gateway.fetch`, `gateway.set_identity`, `png`, `self.assertEqual`, `self.assertFalse`.

## `AdNetworkTests.test_logout_suppresses_late_response_and_untrusted_png_path(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |

반환·실패: None; 불일치AssertionError.

의사코드: 테스트이름의 합성fixture → 실제클래스/함수 호출 → 상태/큐/receipt/오류 불변식 검증.

직접 호출: `AdGateway`, `SimpleNamespace`, `asyncio.Event`, `asyncio.create_task`, `events.append`, `gateway.close`, `gateway.fetch`, `gateway.fetch_png`, `gateway.set_identity`, `release.set`, `self.assertEqual`, `self.assertRaises`, `started.wait`.

## `class AdUiTests(unittest.TestCase)`

기반클래스: unittest.TestCase; 필드 초기값/소유자는파일설명과메서드에서정한다.

## `AdUiTests.setUpClass(cls)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| cls | 없음 | 해당테스트클래스/SDL fixture 소유자. |

반환·실패: None; 테스트실패AssertionError.

의사코드: 함수이름의 owned상태/fixture 준비 → 직접호출 → 공개결과 적용 또는불변식assert → 자기fixture 정리.

직접 호출: `pygame.display.init`, `pygame.display.set_mode`, `pygame.font.init`.

Decorator: `classmethod`.

## `AdUiTests.tearDownClass(cls)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| cls | 없음 | 해당테스트클래스/SDL fixture 소유자. |

반환·실패: None; 테스트실패AssertionError.

의사코드: 함수이름의 owned상태/fixture 준비 → 직접호출 → 공개결과 적용 또는불변식assert → 자기fixture 정리.

직접 호출: `pygame.quit`.

Decorator: `classmethod`.

## `AdUiTests.test_same_layout_refresh_and_image_decode_failure_not_displayed(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |

반환·실패: None; 불일치AssertionError.

의사코드: 테스트이름의 합성fixture → 실제클래스/함수 호출 → 상태/큐/receipt/오류 불변식 검증.

직접 호출: `Controller`, `InputRouter`, `InputRouter().route`, `NetworkStub`, `ScreenRenderer`, `build_layout`, `controller.ads.mark_displayed`, `controller.game.apply_identity`, `controller.handle_network_event`, `controller.request_ad`, `controller.screen_model`, `decision`, `load_config`, `player`, `png`, `pygame.display.get_surface`, `pygame.event.Event`, `renderer.render`, `self.assertEqual`, `self.assertNotIn`, `self.assertTrue`.

## 상태·값 출처

지역 변수는 입력·기존 설정·검증한 공개응답·monotonic시간 또는 자기fixture에서 얻으며 해당함수/클래스가 쓴다. 전역/타이머/큐/fixture의 주요 초기값과 쓰기 소유자는 위 파일설명에 기록한다. 실제env값·계정암호·cookie·CSRF토큰은기록하지않는다.

## 내부 fixture helper

- `png.chunk(name, body)`: 해당테스트의입력·가짜응답/task를 준비/반환한다. 외부서버/실수업DB를호출하지않고 enclosing테스트가수명/결과를소유한다.
- `AdNetworkTests.test_existing_session_csrf_post_and_same_origin_png.Session.get(self, url, **options)`: 해당테스트의입력·가짜응답/task를 준비/반환한다. 외부서버/실수업DB를호출하지않고 enclosing테스트가수명/결과를소유한다.
- `AdNetworkTests.test_existing_session_csrf_post_and_same_origin_png.request_json(method, path, **kwargs)`: 해당테스트의입력·가짜응답/task를 준비/반환한다. 외부서버/실수업DB를호출하지않고 enclosing테스트가수명/결과를소유한다.
- `AdNetworkTests.test_logout_suppresses_late_response_and_untrusted_png_path.request_json(*args, **kwargs)`: 해당테스트의입력·가짜응답/task를 준비/반환한다. 외부서버/실수업DB를호출하지않고 enclosing테스트가수명/결과를소유한다.
