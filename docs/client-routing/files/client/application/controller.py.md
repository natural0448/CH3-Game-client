# client/application/controller.py

기존 사용자 의도/worker 결과를 owned 상태로 번역한다. 마을 광고의 실제 표시 뒤 노출을 요청하고, 클릭이 임시 실패하면 실제 클릭을 기억한 상태에서 다음 성공 표시 프레임에 같은 결정을 재전송한다. 현재 결과의 player/request/decision/slot/type 상관관계가 맞은 인증 실패만 기존 logout 경로로 처리한다. app/game/query/ads 상태는 Controller의 main thread가 소유하며 HTTP를 직접 기다리지 않는다. 자동 새 선택은 connected/ready/열린 조회 패널 없음 및 슬롯 유지/확인 조건을 적용한다.

직접 호출 기대 계약: UI/상태 helper는 각 짝 문서의 반환 계약을 따른다. worker.submit은접수bool, HTTP/JSON helper는공개dict 또는공개오류, read_ad_event는id/type/created dict, emit은queue전달, create_task는Task, Pygame draw/decode는Surface/표시receipt, fixture Web은bytes이다. 하위 계층 내부를 복제하지 않는다.

## `class Controller`

기반클래스: ; 필드 초기값/소유자는파일설명과메서드에서정한다.

## `Controller.__init__(self, network: NetworkPort)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |
| network | 없음 | 기존 NetworkPort queue 구현. |

반환·실패: None.

의사코드: 기존생성자입력에서owned상태/멤버 초기화.

직접 호출: `AdStore`, `ApplicationState`, `GameState`, `QueryStore`.

## `Controller.screen_model(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |

반환·실패: ScreenModel.

의사코드: owned app/game/query/ads를 읽기전용뷰로복사.

직접 호출: `ApplicationView`, `GameView`, `LoginView`, `QueryView`, `ScreenModel`, `copy.deepcopy`, `len`, `player.copy`, `self.ads.views`, `self.game.online_label`, `self.game.own.copy`, `self.game.players.values`, `self.queries.can_request`, `self.queries.slots.items`, `tuple`.

## `Controller.login(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |

반환·실패: None.

의사코드: 로그인입력/phase → 공개login요청 → 비밀입력즉시비움 → worker접수후상태reset.

직접 호출: `draft.username.strip`, `self.ads.reset`, `self.game.clear`, `self.network.submit`, `self.queries.reset`.

## `Controller.logout(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |

반환·실패: None.

의사코드: 현재Player/phase → 기존worker logout접수 → logging_out.

직접 호출: `self.network.submit`.

## `Controller.command(self, name)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |
| name | 없음 | 게임command 이름 또는 내부 식별자. |

반환·실패: None.

의사코드: game.command의기존명령생성 → worker접수/거절시cancel.

직접 호출: `self.game.cancel_submission`, `self.game.command`, `self.network.submit`.

## `Controller.request_query(self, kind)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |
| kind | 없음 | 조회종류/내부코드. |

반환·실패: None.

의사코드: 현재로그인 → query.request → 다른panel닫기 → queue접수/취소.

직접 호출: `self.network.submit`, `self.queries.cancel`, `self.queries.close_others`, `self.queries.request`.

## `Controller.request_ad(self, slot_id, now=None)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |
| slot_id | 없음 | 계약 SLOTS의 village-board/lobby-banner. |
| now | None | monotonic초; None이면현재시간. 테스트는명시한시각. |

반환·실패: None.

의사코드: 현재Player/phase → AdSlot.request → queue접수/취소상태.

직접 호출: `self.network.submit`, `slot.request`, `time.monotonic`.

## `Controller.tick_ads(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |

반환·실패: None.

의사코드: 게임connected/ready/공개visible 상태 → idle 또는 새 선택이 허용된 ready에 request_ad.

직접 호출: `any`, `self.ads.slots.items`, `self.queries.slots.values`, `self.request_ad`, `slot.can_request`, `time.monotonic`.

## `Controller.request_ad_event(self, slot_id, event_type, now=None)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |
| slot_id | 없음 | 계약 SLOTS의 village-board/lobby-banner. |
| event_type | 없음 | impression/click 문자열. |
| now | None | monotonic초; None이면현재시간. 테스트는명시한시각. |

반환·실패: 접수bool.

의사코드: 게임세션/명령/패널/종료상태 → 슬롯request_event → worker.submit; 큐실패는2초재시도.

직접 호출: `any`, `self.ads.slots.get`, `self.network.submit`, `self.queries.slots.values`, `slot.accept_event`, `slot.request_event`, `time.monotonic`.

## `Controller.confirm_ad_display(self, receipts, failures=None, now=None)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |
| receipts | 없음 | 현재성공표시slot→decision_id dict. |
| failures | None | 현재decode실패slot→decision_id dict 또는None. 표시확인은아니다. |
| now | None | monotonic초; None이면현재시간. 테스트는명시한시각. |

반환·실패: None.

의사코드: 현재 프레임 receipt/failure를 AdStore에 적용 → 표시된 마을의 노출/실제 클릭 재시도.

직접 호출: `self.ads.mark_displayed`, `self.request_ad_event`, `time.monotonic`.

## `Controller.handle_intent(self, intent)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |
| intent | 없음 | InputRouter의공개사용자의도dict. |

반환·실패: None.

의사코드: 공개사용자의도kind를기존상태/명령/광고요청으로분기.

직접 호출: `''.join`, `char.isprintable`, `draft.clear`, `intent.get`, `len`, `max`, `self.command`, `self.login`, `self.logout`, `self.network.stop`, `self.queries.set_filter`, `self.queries.turn_page`, `self.request_ad`, `self.request_ad_event`, `self.request_query`, `sources.index`, `tuple`.

## `Controller.handle_network_event(self, event)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |
| event | 없음 | 공개dict queue결과; slot/player/request/decision/type 상관관계 검사. |

반환·실패: None.

의사코드: kind별 owned상태 처리 → ad_event 상관관계 확인 → 현재 needs_login이면 광고초기화/기존logout.

직접 호출: `ERROR_MESSAGES.get`, `event.get`, `result.get`, `self.ads.reset`, `self.ads.slots.get`, `self.app.clear_account`, `self.app.remember_ws`, `self.game.apply_error`, `self.game.apply_identity`, `self.game.apply_snapshot`, `self.game.apply_state`, `self.game.apply_status`, `self.game.clear`, `self.logout`, `self.queries.accept`, `self.queries.reset`, `slot.accept`, `slot.accept_event`, `time.monotonic`.

## 상태·값 출처

지역 변수는 입력·기존 설정·검증한 공개응답·monotonic시간 또는 자기fixture에서 얻으며 해당함수/클래스가 쓴다. 전역/타이머/큐/fixture의 주요 초기값과 쓰기 소유자는 위 파일설명에 기록한다. 실제env값·계정암호·cookie·CSRF토큰은기록하지않는다.
