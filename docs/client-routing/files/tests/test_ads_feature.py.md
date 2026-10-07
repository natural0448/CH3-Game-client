# tests/test_ads_feature.py

## 22일차 이미지 광고 최종 반영

AdStateTests는15초/이전응답/계정ID/receipt 일치/공개 계약을, AdNetworkTests는 기존 세션CSRF·동일 origin PNG·logout 늦은 응답 억제를, AdUiTests는 decode실패 receipt없음·성공flip receipt·refresh hit를 검증한다. png fixture는 stdlib zlib/CRC로1×1 PNG를 만들고 실제 계정/키를 사용하지 않는다. SDL dummy 환경에서만 UI test를 실행한다.

클래스 계약: `class NetworkStub`, `class AdStateTests(unittest.TestCase)`, `class AdNetworkTests(unittest.IsolatedAsyncioTestCase)`, `class AdUiTests(unittest.TestCase)`.


### `png()`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|

반환·실패: 코드 반환 식: `b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', 1, 1, 8, 6, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(b'\x00@\x90@\xff')) + chunk(b'IEND', b'')`, `struct.pack('>I', len(body)) + name + body + struct.pack('>I', zlib.crc32(name + body))`.

의사코드: 기존 입력·상태 검사 → 직접 호출 → 현재 결과/상태 전달; 이미지 추가 책임은 위 파일 설명 참조.

직접 호출: `chunk`, `struct.pack`, `zlib.crc32`, `zlib.compress`, `len`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `png.chunk(name, body)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| name | 없음 | fixture 로그 식별자/테스트 helper 문자열. |
| body | 없음 | 기존 body 입력; 아래 동작·직접 호출과 기존 계약 참조. |

반환·실패: 코드 반환 식: `struct.pack('>I', len(body)) + name + body + struct.pack('>I', zlib.crc32(name + body))`.

의사코드: 기존 입력·상태 검사 → 직접 호출 → 현재 결과/상태 전달; 이미지 추가 책임은 위 파일 설명 참조.

직접 호출: `struct.pack`, `zlib.crc32`, `len`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `decision()`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|

반환·실패: 코드 반환 식: `{'decision_id': '00000000-0000-4000-8000-000000000001', 'campaign_id': 'forest-tools', 'title': '숲 도구점', 'body': '마을의 도구', 'slot_id': 'village-board', 'creative_path': '/static/ads/creatives/forest-tools.png', 'bid_amount': 30, 'policy_version': 'highest-bid/v1'}`.

의사코드: 기존 입력·상태 검사 → 직접 호출 → 현재 결과/상태 전달; 이미지 추가 책임은 위 파일 설명 참조.

직접 호출: 없음. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `NetworkStub.__init__(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |

반환·실패: None.

의사코드: 해당 파일 책임에 정의한 소유 상태/fixture를 초기화·정리 또는 교체.

직접 호출: 없음. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `NetworkStub.submit(self, request)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |
| request | 없음 | 해당 계층의 Django HttpRequest 또는 public correlated queue dict. |

반환·실패: 코드 반환 식: `True`.

의사코드: 기존 입력·상태 검사 → 직접 호출 → 현재 결과/상태 전달; 이미지 추가 책임은 위 파일 설명 참조.

직접 호출: `self.requests.append`, `dict`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `AdStateTests.test_retention_stale_identity_and_display_receipt(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |

반환·실패: None; 실패 AssertionError.

의사코드: 파일 책임에 적힌 시나리오의 fixture 준비 → 실제 함수 호출 → assertion → fixture 정리.

직접 호출: `AdStore`, `slot.request`, `self.assertFalse`, `self.assertTrue`, `self.assertIsNone`, `store.mark_displayed`, `self.assertIsNotNone`, `store.reset`, `decision`, `png`, `slot.accept`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `AdStateTests.test_public_contract_and_unsafe_values(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |

반환·실패: None; 실패 AssertionError.

의사코드: 파일 책임에 적힌 시나리오의 fixture 준비 → 실제 함수 호출 → assertion → fixture 정리.

직접 호출: `read_decision`, `self.assertNotIn`, `self.assertIsNone`, `decision`, `self.subTest`, `self.assertRaises`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `AdNetworkTests.test_existing_session_csrf_post_and_same_origin_png(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |

반환·실패: None; 실패 AssertionError.

의사코드: 파일 책임에 적힌 시나리오의 fixture 준비 → 실제 함수 호출 → assertion → fixture 정리.

직접 호출: `SimpleNamespace`, `AdGateway`, `gateway.set_identity`, `self.assertEqual`, `self.assertFalse`, `calls.append`, `decision`, `gateway.fetch`, `png`, `gateway.close`, `Response`, `Session`, `events.append`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `AdNetworkTests.test_existing_session_csrf_post_and_same_origin_png.Session.get(self, url, **options)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |
| url | 없음 | 검사할 fixture HTTP URL. |
| options | 없음 | 기존 options 입력; 아래 동작·직접 호출과 기존 계약 참조. |

반환·실패: 코드 반환 식: `Response(content_type='image/png', raw=png())`.

의사코드: 기존 입력·상태 검사 → 직접 호출 → 현재 결과/상태 전달; 이미지 추가 책임은 위 파일 설명 참조.

직접 호출: `calls.append`, `Response`, `png`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `AdNetworkTests.test_existing_session_csrf_post_and_same_origin_png.request_json(method, path, **kwargs)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| method | 없음 | 기존 method 입력; 아래 동작·직접 호출과 기존 계약 참조. |
| path | 없음 | 허용된 상대 PNG URL 또는 fixture HTTP 경로; 외부 URL은 PNG fetch 금지. |
| kwargs | 없음 | 기존 kwargs 입력; 아래 동작·직접 호출과 기존 계약 참조. |

반환·실패: 코드 반환 식: `decision()`.

의사코드: 기존 입력·상태 검사 → 직접 호출 → 현재 결과/상태 전달; 이미지 추가 책임은 위 파일 설명 참조.

직접 호출: `calls.append`, `decision`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `AdNetworkTests.test_logout_suppresses_late_response_and_untrusted_png_path(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |

반환·실패: None; 실패 AssertionError.

의사코드: 파일 책임에 적힌 시나리오의 fixture 준비 → 실제 함수 호출 → assertion → fixture 정리.

직접 호출: `asyncio.Event`, `SimpleNamespace`, `AdGateway`, `gateway.set_identity`, `asyncio.create_task`, `release.set`, `self.assertEqual`, `started.set`, `gateway.fetch`, `started.wait`, `gateway.close`, `self.assertRaises`, `release.wait`, `events.append`, `gateway.fetch_png`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `AdNetworkTests.test_logout_suppresses_late_response_and_untrusted_png_path.request_json(*args, **kwargs)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| args | 없음 | 기존 args 입력; 아래 동작·직접 호출과 기존 계약 참조. |
| kwargs | 없음 | 기존 kwargs 입력; 아래 동작·직접 호출과 기존 계약 참조. |

반환·실패: 코드 반환 식: `{'ad': None}`.

의사코드: 기존 입력·상태 검사 → 직접 호출 → 현재 결과/상태 전달; 이미지 추가 책임은 위 파일 설명 참조.

직접 호출: `started.set`, `release.wait`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `AdUiTests.setUpClass(cls)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| cls | 없음 | 테스트 클래스; fixture 수명 관리. |

반환·실패: None.

의사코드: 해당 파일 책임에 정의한 소유 상태/fixture를 초기화·정리 또는 교체.

직접 호출: `pygame.display.init`, `pygame.font.init`, `pygame.display.set_mode`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `AdUiTests.tearDownClass(cls)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| cls | 없음 | 테스트 클래스; fixture 수명 관리. |

반환·실패: None.

의사코드: 해당 파일 책임에 정의한 소유 상태/fixture를 초기화·정리 또는 교체.

직접 호출: `pygame.quit`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `AdUiTests.test_same_layout_refresh_and_image_decode_failure_not_displayed(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |

반환·실패: None; 실패 AssertionError.

의사코드: 파일 책임에 적힌 시나리오의 fixture 준비 → 실제 함수 호출 → assertion → fixture 정리.

직접 호출: `Controller`, `controller.game.apply_identity`, `controller.request_ad`, `controller.handle_network_event`, `ScreenRenderer`, `renderer.render`, `self.assertNotIn`, `png`, `self.assertEqual`, `controller.ads.mark_displayed`, `self.assertTrue`, `build_layout`, `pygame.event.Event`, `InputRouter().route`, `NetworkStub`, `player`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.
