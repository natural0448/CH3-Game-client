# client/application/ads.py

## 22일차 이미지 광고 최종 반영

AdView는 frozen slot/status/message/decision/image_bytes/can_request/displayed 읽기 값이다. AdSlot 초기 idle/decision·image_bytes·request_id=None/next_request_at=0/displayed=False. request마다 uuid4hex와15초 next_request_at를 생성하고 예전 광고를 지운다. 응답은 pending 상태·슬롯·request ID·현재 player ID가 모두 일치할 때만 accept한다. AdStore.slots는 두 슬롯 dict를 소유하며 reset/views/flip후 receipt 표시 확인을 담당한다. deep copy로 network/renderer의 snapshot 변경을 격리한다. 노출 저장은 하지 않는다.

클래스 계약: `class AdView`, `class AdSlot`, `class AdStore`.


### `AdSlot.__init__(self, slot_id)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |
| slot_id | 없음 | village-board 또는 lobby-banner. |

반환·실패: None.

의사코드: 해당 파일 책임에 정의한 소유 상태/fixture를 초기화·정리 또는 교체.

직접 호출: `self.clear`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `AdSlot.clear(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |

반환·실패: None.

의사코드: 해당 파일 책임에 정의한 소유 상태/fixture를 초기화·정리 또는 교체.

직접 호출: 없음. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `AdSlot.request(self, player_id, now)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |
| player_id | 없음 | 현재 로그인 Player의 정수 ID; 네트워크 응답 상관관계 검사 전용. |
| now | 없음 | monotonic 초; None이면 time.monotonic. 테스트는 명시적 시간 사용. |

반환·실패: request dict 또는 cooldown/pending None.

의사코드: pending/15초 확인 → uuid request → next_request_at → 상태 pending·snapshot 비우기 → 큐 입력.

직접 호출: `uuid.uuid4`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `AdSlot.accept(self, event, player_id)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |
| event | 없음 | public network event; slot/request/player ID 일치해야 수락. |
| player_id | 없음 | 현재 로그인 Player의 정수 ID; 네트워크 응답 상관관계 검사 전용. |

반환·실패: 처리 bool; 상관관계 불일치 False.

의사코드: pending·slot·request·현재계정 일치 → 실패/없음/선택 상태 → 선택 deepcopy.

직접 호출: `event.get`, `copy.deepcopy`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `AdSlot.view(self, now)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |
| now | 없음 | monotonic 초; None이면 time.monotonic. 테스트는 명시적 시간 사용. |

반환·실패: AdView.

의사코드: 현재 snapshot 복제 → pending/cooldown에서 can_request 계산 → frozen view.

직접 호출: `AdView`, `copy.deepcopy`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `AdStore.__init__(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |

반환·실패: None.

의사코드: 해당 파일 책임에 정의한 소유 상태/fixture를 초기화·정리 또는 교체.

직접 호출: `AdSlot`, `sorted`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `AdStore.reset(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |

반환·실패: None.

의사코드: 해당 파일 책임에 정의한 소유 상태/fixture를 초기화·정리 또는 교체.

직접 호출: `self.slots.values`, `slot.clear`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `AdStore.views(self, now=None)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |
| now | `None` | monotonic 초; None이면 time.monotonic. 테스트는 명시적 시간 사용. |

반환·실패: dict[str,AdView].

의사코드: now None이면 monotonic → 슬롯별 view.

직접 호출: `time.monotonic`, `slot.view`, `self.slots.items`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `AdStore.mark_displayed(self, receipts)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |
| receipts | 없음 | 실제 render/flip 성공 후 slot→현재 decision ID mapping. |

반환·실패: None; 이후 노출 API는 호출하지 않음.

의사코드: receipt별 현재 ready 결정 ID 비교 → 일치 슬롯 displayed=True.

직접 호출: `receipts.items`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.
