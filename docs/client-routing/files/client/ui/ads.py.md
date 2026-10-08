# client/ui/ads.py

메인 스레드에서 공개 PNG를 decode/cache하고 기존 두 광고 카드를 그린다. images 초기값은빈dict이며 슬롯→(decision_id,Surface), failures는 현재 프레임의 decode 실패 slot→decision_id이다. draw마다 failures를 초기화하고 실패 광고는 receipt에 넣지 않는다. 마을 카드의 노출/클릭 완료 및 영구 거절의 광고 새 요청 필요를 표시한다. 실제 HTTP는 호출하지 않는다. lobby는 기존 소재/금액/ID 표시를 유지한다.

직접 호출 기대 계약: UI/상태 helper는 각 짝 문서의 반환 계약을 따른다. worker.submit은접수bool, HTTP/JSON helper는공개dict 또는공개오류, read_ad_event는id/type/created dict, emit은queue전달, create_task는Task, Pygame draw/decode는Surface/표시receipt, fixture Web은bytes이다. 하위 계층 내부를 복제하지 않는다.

## `class AdsRenderer`

기반클래스: ; 필드 초기값/소유자는파일설명과메서드에서정한다.

## `AdsRenderer.__init__(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |

반환·실패: None.

의사코드: 기존생성자입력에서owned상태/멤버 초기화.

직접 호출: .

## `AdsRenderer.image(self, slot)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |
| slot | 없음 | 슬롯 AdView 또는AdSlot. |

반환·실패: Surface 또는None; decode예외.

의사코드: main thread 검사 → 빈path cache제거 또는 현재ID cache → PNG decode/cache.

직접 호출: `ValueError`, `io.BytesIO`, `pygame.image.load`, `pygame.image.load(io.BytesIO(slot.image_bytes)).convert_alpha`, `self.images.get`, `self.images.pop`, `threading.current_thread`, `threading.main_thread`.

## `AdsRenderer.draw(self, painter, ads, authenticated)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당인스턴스; 상태 소유자. |
| painter | 없음 | 메인스레드의 Painter/Layout. |
| ads | 없음 | frozen슬롯뷰dict. |
| authenticated | 없음 | 현재게임로그인bool. |

반환·실패: 성공slot→decision_id dict; failures 별도 owned dict.

의사코드: 현재frame failures 초기화 → 카드/소재 → decode실패 기록 또는 draw/receipt → 마을 진행/거절 표시.

직접 호출: `ads.items`, `painter.button`, `painter.canvas.blit`, `painter.card`, `painter.text`, `painter.wrapped`, `pygame.Rect`, `pygame.transform.scale`, `self.image`, `self.images.clear`.

## 상태·값 출처

지역 변수는 입력·기존 설정·검증한 공개응답·monotonic시간 또는 자기fixture에서 얻으며 해당함수/클래스가 쓴다. 전역/타이머/큐/fixture의 주요 초기값과 쓰기 소유자는 위 파일설명에 기록한다. 실제env값·계정암호·cookie·CSRF토큰은기록하지않는다.
