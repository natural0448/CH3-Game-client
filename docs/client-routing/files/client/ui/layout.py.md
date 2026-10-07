# client/ui/layout.py

## 책임과 상수

draw와 hit test가 공유하는 불변 logical Layout이다. `CANVAS=(1100,880)`, control/slot/viewport Rect는 `_controls`와 `build_layout`에서만 생성한다. load·metrics·lake 진입과 각 refresh/close Rect도 같은 control 사전에 있다.

## 함수와 메서드

`_controls()` — 로그인, 명령, 기존 조회, load/metrics/lake 버튼과 패널 refresh/close를 포함한 고정 logical Rect dict를 반환한다. lobby의 둘째 줄에 load/metrics, 셋째 줄에 delivery/lake를 둔다. delivery=(366,758,178,28), lake=(550,758,98,28), lake_refresh=(386,174,134,32), lake_close=(530,174,104,32)다. 다른 slot/ad_slot/world Rect는 유지한다.

`Layout.viewport(self)` — 실제 `screen_size`에 맞춘 letterbox 크기와 offset을 계산한다.

`Layout.to_canvas(self, position)` — 화면 mouse 좌표를 logical canvas 좌표로 변환한다.

`Layout.hit_test(self, position, open_panels)` — 열린 analytics/history/actions/ingest/windows/load/metrics/lake 패널 control을 우선한 뒤 일반 control 이름을 반환한다. lake_ control은 해당 패널이 닫힌 상태의 일반 hit 대상에서 제외한다.

`build_layout(screen_size)` — control, 광고 slot, world/panel Rect가 든 frozen Layout을 만든다.

직접 호출: `pygame.Rect`, 내장 `min/max/int`.

## 22일차 이미지 광고 최종 반영

기존 ad_slots anchor Rect(40,740,278,58)/(710,788,342,24)를 보존한다. 실제 카드 ad_cards는 village-board Rect(24,656,310,168), lobby-banner Rect(688,786,388,42)다. refresh Rect는(226,664,96,28)/(1018,794,48,24)이며 그림과 hit-test가 같은 controls를 사용한다. Layout.ad_cards는 build_layout이 매번 소유해 생성한다.

클래스 계약: `class Layout`.


### `_controls()`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|

반환·실패: 코드 반환 식: `{'username': pygame.Rect(24, 96, 220, 40), 'password': pygame.Rect(256, 96, 220, 40), 'login': pygame.Rect(488, 96, 118, 40), 'logout': pygame.Rect(618, 96, 118, 40), 'up': pygame.Rect(830, 312, 92, 42), 'left': pygame.Rect(728, 364, 92, 42), 'down': pygame.Rect(830, 364, 92, 42), 'right': pygame.Rect(932, 364, 92, 42), 'gather': pygame.Rect(710, 418, 166, 42), 'train': pygame.Rect(888, 418, 166, 42), 'history': pygame.Rect(894, 494, 160, 32), 'delivery': pygame.Rect(366, 758, 178, 28), 'lake': pygame.Rect(550, 758, 98, 28), 'delivery_api': pygame.Rect(904, 578, 144, 28), 'analytics': pygame.Rect(366, 690, 66, 28), 'actions': pygame.Rect(438, 690, 66, 28), 'ingest': pygame.Rect(510, 690, 66, 28), 'windows': pygame.Rect(582, 690, 66, 28), 'load': pygame.Rect(366, 724, 138, 28), 'metrics': pygame.Rect(510, 724, 138, 28), 'api_source': pygame.Rect(710, 612, 230, 28), 'api_up': pygame.Rect(952, 612, 42, 28), 'api_down': pygame.Rect(1006, 612, 42, 28), 'analytics_refresh': pygame.Rect(420, 174, 100, 32), 'analytics_close': pygame.Rect(530, 174, 104, 32), 'analytics_previous': pygame.Rect(420, 588, 92, 30), 'analytics_next': pygame.Rect(526, 588, 92, 30), 'history_close': pygame.Rect(530, 174, 104, 32), 'history_previous': pygame.Rect(420, 588, 92, 30), 'history_next': pygame.Rect(526, 588, 92, 30), 'actions_refresh': pygame.Rect(420, 174, 100, 32), 'actions_close': pygame.Rect(530, 174, 104, 32), 'actions_previous': pygame.Rect(420, 588, 92, 30), 'actions_next': pygame.Rect(526, 588, 92, 30), 'ingest_refresh': pygame.Rect(386, 174, 134, 32), 'ingest_close': pygame.Rect(530, 174, 104, 32), 'windows_refresh': pygame.Rect(386, 174, 134, 32), 'windows_close': pygame.Rect(530, 174, 104, 32), 'windows_filter_all': pygame.Rect(56, 260, 92, 30), 'windows_filter_tumbling': pygame.Rect(158, 260, 176, 30), 'windows_filter_sliding': pygame.Rect(344, 260, 176, 30), 'load_refresh': pygame.Rect(386, 174, 134, 32), 'load_close': pygame.Rect(530, 174, 104, 32), 'metrics_refresh': pygame.Rect(386, 174, 134, 32), 'metrics_close': pygame.Rect(530, 174, 104, 32), 'lake_refresh': pygame.Rect(386, 174, 134, 32), 'lake_close': pygame.Rect(530, 174, 104, 32), 'ad_village_refresh': pygame.Rect(226, 664, 96, 28), 'ad_lobby_refresh': pygame.Rect(1018, 794, 48, 24)}`.

의사코드: 기존 입력·상태 검사 → 직접 호출 → 현재 결과/상태 전달; 이미지 추가 책임은 위 파일 설명 참조.

직접 호출: `pygame.Rect`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `Layout.viewport(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |

반환·실패: 코드 반환 식: `(size, ((width - size[0]) // 2, (height - size[1]) // 2))`.

의사코드: 기존 입력·상태 검사 → 직접 호출 → 현재 결과/상태 전달; 이미지 추가 책임은 위 파일 설명 참조.

직접 호출: `min`, `max`, `int`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `Layout.to_canvas(self, position)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |
| position | 없음 | 기존 position 입력; 아래 동작·직접 호출과 기존 계약 참조. |

반환·실패: 코드 반환 식: `((position[0] - offset[0]) * CANVAS[0] / size[0], (position[1] - offset[1]) * CANVAS[1] / size[1])`.

의사코드: 기존 입력·상태 검사 → 직접 호출 → 현재 결과/상태 전달; 이미지 추가 책임은 위 파일 설명 참조.

직접 호출: `self.viewport`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `Layout.hit_test(self, position, open_panels)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |
| position | 없음 | 기존 position 입력; 아래 동작·직접 호출과 기존 계약 참조. |
| open_panels | 없음 | 기존 open_panels 입력; 아래 동작·직접 호출과 기존 계약 참조. |

반환·실패: 코드 반환 식: `next((name for name, rect in self.controls.items() if not name.startswith(('analytics_', 'history_', 'actions_', 'ingest_', 'windows_', 'load_', 'metrics_', 'lake_')) and rect.collidepoint(point)), None)`, `next((name for name, rect in self.controls.items() if name.startswith(prefix) and rect.collidepoint(point)), None)`.

의사코드: 기존 입력·상태 검사 → 직접 호출 → 현재 결과/상태 전달; 이미지 추가 책임은 위 파일 설명 참조.

직접 호출: `self.to_canvas`, `next`, `self.panel_rect.collidepoint`, `self.controls.items`, `rect.collidepoint`, `name.startswith`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `build_layout(screen_size)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| screen_size | 없음 | 기존 screen_size 입력; 아래 동작·직접 호출과 기존 계약 참조. |

반환·실패: 코드 반환 식: `Layout(screen_size=screen_size, controls=_controls(), slots={'village-board': pygame.Rect(24, 656, 310, 78), 'lobby-banner': pygame.Rect(350, 656, 314, 158)}, ad_slots={'village-ad-slot': pygame.Rect(40, 740, 278, 58), 'lobby-ad-slot': pygame.Rect(710, 788, 342, 24)}, world_rect=pygame.Rect(22, 150, 644, 484), panel_rect=pygame.Rect(36, 162, 616, 470), ad_cards={'village-board': pygame.Rect(24, 656, 310, 168), 'lobby-banner': pygame.Rect(688, 786, 388, 42)})`.

의사코드: 기존 입력·상태 검사 → 직접 호출 → 현재 결과/상태 전달; 이미지 추가 책임은 위 파일 설명 참조.

직접 호출: `Layout`, `_controls`, `pygame.Rect`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.
