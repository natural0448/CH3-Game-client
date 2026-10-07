# client/application/controller.py

## 책임과 직접 의존성

사용자 intent와 network event를 유일한 상태 쓰기 소유자에게 전달한다. 구체 worker 대신 `NetworkPort`를 받고 `GameState`, `QueryStore`, `ApplicationState`를 조정한다.

## 메서드

`Controller.__init__(self, network: NetworkPort)` — port와 세 상태 객체를 저장한다.

`Controller.screen_model(self)`

```text
ApplicationState·GameState·QueryStore를 복사
비밀번호 문자열 대신 길이만 LoginView에 기록
조회 page·filter_value를 포함한 frozen ScreenModel 반환
```

`Controller.login(self)` — 입력 검사 → password 지역 요청 생성 → port.submit → 상태·조회 초기화; 제출 후 password를 비운다.

`Controller.logout(self)` — 계정과 phase를 확인해 `{kind: logout}`을 제출하고 logging_out을 기록한다.

`Controller.command(self, name)` — `GameState.command` 결과만 제출하며 queue 실패 시 pending을 취소한다.

`Controller.request_query(self, kind)` — 계정·phase 검사 → `QueryStore.request` → port 제출; GET 종류만 생성한다.

`Controller.handle_intent(self, intent)`

```text
quit/focus/text/login/logout/command/query/panel page/filter/API 의도를 구분
panel_filter는 QueryStore.set_filter에만 전달하여 새 GET을 만들지 않음
해당 공개 메서드 또는 상태 소유자만 호출
Pygame·aiohttp를 호출하지 않음
```

`Controller.handle_network_event(self, event)`

```text
status/identity/state/snapshot/error는 GameState에 전달
조회 결과는 QueryStore.accept에 전달
로그인 종료·worker 종료는 계정 상태를 초기화
표시 문구와 최근 WS 요약만 ApplicationState에 기록
```

파라미터는 InputRouter 또는 worker queue에서 온 credential-free dict다. 직접 호출: `NetworkPort.submit/stop`, `GameState`, `QueryStore`, `copy.deepcopy`.

## 22일차 이미지 광고 최종 반영

Controller가 AdStore를 소유한다. screen_model은 deep-copied AdView mapping도 읽기 모델에 포함한다. request_ad는 현재 계정/종료 상태/슬롯 cooldown을 검사하고 request ID/player ID로 큐에 제출한다. 큐 실패는 retry가능 error로 돌린다. tick_ads는 game.ready/connected인 idle 슬롯만 최초 요청한다. ad_refresh intent와 correlated ad event를 처리하고 로그인/로그아웃/종료 시 reset한다. 기존 게임/analytics 상태는 광고 응답으로 쓰지 않는다.

클래스 계약: `class Controller`.


### `Controller.__init__(self, network: NetworkPort)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |
| network | 없음 | 기존 NetworkPort; submit은 큐 접수 bool. |

반환·실패: None.

의사코드: 해당 파일 책임에 정의한 소유 상태/fixture를 초기화·정리 또는 교체.

직접 호출: `ApplicationState`, `GameState`, `QueryStore`, `AdStore`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `Controller.screen_model(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |

반환·실패: 코드 반환 식: `ScreenModel(app=app, game=game, queries=queries, ads=self.ads.views())`.

의사코드: 기존 입력·상태 검사 → 직접 호출 → 현재 결과/상태 전달; 이미지 추가 책임은 위 파일 설명 참조.

직접 호출: `ApplicationView`, `GameView`, `ScreenModel`, `QueryView`, `tuple`, `LoginView`, `self.game.online_label`, `self.queries.slots.items`, `self.ads.views`, `self.game.own.copy`, `copy.deepcopy`, `self.queries.can_request`, `len`, `player.copy`, `self.game.players.values`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `Controller.login(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |

반환·실패: None.

의사코드: 기존 입력·상태 검사 → 직접 호출 → 현재 결과/상태 전달; 이미지 추가 책임은 위 파일 설명 참조.

직접 호출: `self.network.submit`, `draft.username.strip`, `self.game.clear`, `self.queries.reset`, `self.ads.reset`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `Controller.logout(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |

반환·실패: None.

의사코드: 기존 입력·상태 검사 → 직접 호출 → 현재 결과/상태 전달; 이미지 추가 책임은 위 파일 설명 참조.

직접 호출: `self.network.submit`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `Controller.command(self, name)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |
| name | 없음 | fixture 로그 식별자/테스트 helper 문자열. |

반환·실패: None.

의사코드: 기존 입력·상태 검사 → 직접 호출 → 현재 결과/상태 전달; 이미지 추가 책임은 위 파일 설명 참조.

직접 호출: `self.game.command`, `self.network.submit`, `self.game.cancel_submission`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `Controller.request_query(self, kind)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |
| kind | 없음 | 기존 kind 입력; 아래 동작·직접 호출과 기존 계약 참조. |

반환·실패: None.

의사코드: 기존 입력·상태 검사 → 직접 호출 → 현재 결과/상태 전달; 이미지 추가 책임은 위 파일 설명 참조.

직접 호출: `self.queries.request`, `self.queries.close_others`, `self.network.submit`, `self.queries.cancel`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `Controller.request_ad(self, slot_id, now=None)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |
| slot_id | 없음 | village-board 또는 lobby-banner. |
| now | `None` | monotonic 초; None이면 time.monotonic. 테스트는 명시적 시간 사용. |

반환·실패: None.

의사코드: 계정/종료상태 → 슬롯 request → 큐 submit → queue 실패시 retry가능 error.

직접 호출: `slot.request`, `time.monotonic`, `self.network.submit`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `Controller.tick_ads(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |

반환·실패: None.

의사코드: 게임 ready+connected → idle인 슬롯만 최초 request_ad.

직접 호출: `self.ads.slots.items`, `self.request_ad`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `Controller.handle_intent(self, intent)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |
| intent | 없음 | 기존 intent 입력; 아래 동작·직접 호출과 기존 계약 참조. |

반환·실패: None.

의사코드: 기존 입력·상태 검사 → 직접 호출 → 현재 결과/상태 전달; 이미지 추가 책임은 위 파일 설명 참조.

직접 호출: `intent.get`, `draft.clear`, `self.network.stop`, `''.join`, `self.login`, `char.isprintable`, `self.logout`, `self.command`, `self.request_query`, `self.request_ad`, `self.queries.turn_page`, `self.queries.set_filter`, `tuple`, `max`, `len`, `sources.index`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `Controller.handle_network_event(self, event)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |
| event | 없음 | public network event; slot/request/player ID 일치해야 수락. |

반환·실패: None.

의사코드: 기존 입력·상태 검사 → 직접 호출 → 현재 결과/상태 전달; 이미지 추가 책임은 위 파일 설명 참조.

직접 호출: `event.get`, `self.ads.slots.get`, `slot.accept`, `self.game.apply_status`, `self.game.apply_identity`, `self.game.apply_snapshot`, `self.app.remember_ws`, `self.game.apply_state`, `result.get`, `self.game.apply_error`, `ERROR_MESSAGES.get`, `self.queries.accept`, `self.game.clear`, `self.queries.reset`, `self.ads.reset`, `self.app.clear_account`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.
