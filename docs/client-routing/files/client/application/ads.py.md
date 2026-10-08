# client/application/ads.py

별도 접속기 광고 표시·클릭의 상태 책임. 최신 3교시 직접 구현 대상인 게임 request_ad_event와 구별한다. AdView는 frozen 화면 snapshot이고 event_rejected 기본False, 나머지 사건 bool 기본False/event_error 빈 문자열이다. AdSlot.clear 초기값: status=idle, decision/image_bytes/request_id=None, next_request_at/retained_until=0, displayed/image_failed=False. reset_events는 impression/click pending/ok,click_requested,event_rejected=False와 retry_at=0,error=빈 문자열을 설정한다. UUID request_id·15초 요청 간격, 최초 성공 표시에서 retained_until=now+10, 사건 임시 실패의 now+2 retry, 영구 거절의 retained_until/next_request_at=now+2는 main thread가 소유한다. request_event는 마을 게시판만 보내고 실제 click 요청을 기억한다. 저장 확인 전/전송 중/미완료 클릭에서는 같은 결정을 유지한다. AdStore.slots는 계약 SLOTS의 슬롯별 상태다. 표시 실패는 같은 결정 ID의 failure 신호로만 적용한다. 새 광고/로그아웃은 이전 상태를 초기화한다.

직접 호출 기대 계약: UI/상태 helper는 각 짝 문서의 반환 계약을 따른다. worker.submit은접수bool, HTTP/JSON helper는공개dict 또는공개오류, read_ad_event는id/type/created dict, emit은queue전달, create_task는Task, Pygame draw/decode는Surface/표시receipt, fixture Web은bytes이다. 하위 계층 내부를 복제하지 않는다.

## `class AdView`

기반클래스: ; 필드 초기값/소유자는파일설명과메서드에서정한다.

## `class AdSlot`

기반클래스: ; 필드 초기값/소유자는파일설명과메서드에서정한다.

## `AdSlot.__init__(self, slot_id)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |
| slot_id | 없음 | 계약 SLOTS의 village-board/lobby-banner. |

반환·실패: None.

의사코드: 기존생성자입력에서owned상태/멤버 초기화.

직접 호출: `self.clear`.

## `AdSlot.clear(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |

반환·실패: None.

의사코드: 슬롯 selection/타이머/표시 초기화 → reset_events.

직접 호출: `self.reset_events`.

## `AdSlot.reset_events(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |

반환·실패: None.

의사코드: 사건 pending/ok/click_requested/rejected/retry/error 초기화.

직접 호출: .

## `AdSlot.can_request(self, now)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |
| now | 없음 | monotonic초; None이면현재시간. 테스트는명시한시각. |

반환·실패: 허용bool.

의사코드: pending/사건 전송/15초/retained_until 검사 → 준비 광고의 decode·표시·노출·클릭 확인 조건 검사.

직접 호출: .

## `AdSlot.request(self, player_id, now)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |
| player_id | 없음 | 현재게임 Player의공개정수ID. |
| now | 없음 | monotonic초; None이면현재시간. 테스트는명시한시각. |

반환·실패: dict 또는None.

의사코드: can_request → UUID/15초 요청 시각 → 이전 선택/표시/사건 초기화 → 공개 queue request.

직접 호출: `self.can_request`, `self.reset_events`, `uuid.uuid4`.

## `AdSlot.accept(self, event, player_id)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |
| event | 없음 | 공개dict queue결과; slot/player/request/decision/type 상관관계 검사. |
| player_id | 없음 | 현재게임 Player의공개정수ID. |

반환·실패: 처리bool.

의사코드: 선택 결과slot/request/player/status 검사 → error/empty/ready 및 deepcopy 결정/PNG.

직접 호출: `copy.deepcopy`, `event.get`.

## `AdSlot.request_event(self, event_type, player_id, now)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |
| event_type | 없음 | impression/click 문자열. |
| player_id | 없음 | 현재게임 Player의공개정수ID. |
| now | 없음 | monotonic초; None이면현재시간. 테스트는명시한시각. |

반환·실패: dict 또는None.

의사코드: 종류/마을슬롯/ready/실제표시/거절/retry/전송/완료/선행노출 검사 → pending/실제클릭기억 → 공개 사건 queue.

직접 호출: `getattr`, `isinstance`, `setattr`.

## `AdSlot.accept_event(self, event, player_id, now)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |
| event | 없음 | 공개dict queue결과; slot/player/request/decision/type 상관관계 검사. |
| player_id | 없음 | 현재게임 Player의공개정수ID. |
| now | 없음 | monotonic초; None이면현재시간. 테스트는명시한시각. |

반환·실패: 처리bool; 늦은/타계정/이전결과False.

의사코드: 상관관계·pending 검사 → pending해제 → receipt 검증 → ok 또는 임시2초 retry/영구중지·2초 새 선택.

직접 호출: `ValueError`, `bool`, `event.get`, `getattr`, `isinstance`, `read_ad_event`, `setattr`.

## `AdSlot.view(self, now)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |
| now | 없음 | monotonic초; None이면현재시간. 테스트는명시한시각. |

반환·실패: AdView.

의사코드: deepcopy 결정과 can_request/사건 상태로 frozen AdView 구성.

직접 호출: `AdView`, `copy.deepcopy`, `self.can_request`.

## `class AdStore`

기반클래스: ; 필드 초기값/소유자는파일설명과메서드에서정한다.

## `AdStore.__init__(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |

반환·실패: None.

의사코드: 기존생성자입력에서owned상태/멤버 초기화.

직접 호출: `AdSlot`, `sorted`.

## `AdStore.reset(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |

반환·실패: None.

의사코드: 각슬롯clear.

직접 호출: `self.slots.values`, `slot.clear`.

## `AdStore.views(self, now=None)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |
| now | None | monotonic초; None이면현재시간. 테스트는명시한시각. |

반환·실패: dict[str,AdView].

의사코드: now 기본monotonic → 슬롯별 view.

직접 호출: `self.slots.items`, `slot.view`, `time.monotonic`.

## `AdStore.mark_displayed(self, receipts, now=None, failures=None)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |
| receipts | 없음 | 현재성공표시slot→decision_id dict. |
| now | None | monotonic초; None이면현재시간. 테스트는명시한시각. |
| failures | None | 현재decode실패slot→decision_id dict 또는None. 표시확인은아니다. |

반환·실패: None.

의사코드: 현재 ID의 decode실패 반영 → 현재 ID의 성공receipt에 최초10초 retained_until/표시 성공 적용.

직접 호출: `(failures or {}).items`, `receipts.items`, `time.monotonic`.

## 상태·값 출처

지역 변수는 입력·기존 설정·검증한 공개응답·monotonic시간 또는 자기fixture에서 얻으며 해당함수/클래스가 쓴다. 전역/타이머/큐/fixture의 주요 초기값과 쓰기 소유자는 위 파일설명에 기록한다. 실제env값·계정암호·cookie·CSRF토큰은기록하지않는다.
