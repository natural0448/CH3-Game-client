# client/ui/ads.py

## 22일차 이미지 광고 최종 반영

AdsRenderer.images={} 캐시는 슬롯별(decision ID,pygame Surface)이며 main thread에서만 PNG를 decode한다. 카드 theme는 camp-tea warm/나머지 green. village icon64px/lobby32px이며 title/body/금액/decision ID를 선택 snapshot에서 그린다. 이미지 실패는 별도 문구와 receipt 제외. 텍스트 광고는 빈 경로로 이미지 없이 표시한다. authenticated=False이면 cache clear, 로그인 안내. draw는 표시 성공 slot→ID mapping을 반환하고 실제 flip은 상위 renderer가 수행한다.

클래스 계약: `class AdsRenderer`.


### `AdsRenderer.__init__(self)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |

반환·실패: None.

의사코드: 해당 파일 책임에 정의한 소유 상태/fixture를 초기화·정리 또는 교체.

직접 호출: 없음. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `AdsRenderer.image(self, slot)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |
| slot | 없음 | 현재 AdView snapshot 또는 허용 슬롯 ID; 함수 맥락 참조. |

반환·실패: pygame Surface 또는 None(text); decode 예외는 draw 처리.

의사코드: main thread 검사 → text-only cache삭제 → 동일결정cache 또는 PNG bytes decode/cache.

직접 호출: `self.images.get`, `pygame.image.load(io.BytesIO(slot.image_bytes)).convert_alpha`, `threading.current_thread`, `threading.main_thread`, `self.images.pop`, `ValueError`, `pygame.image.load`, `io.BytesIO`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `AdsRenderer.draw(self, painter, ads, authenticated)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |
| painter | 없음 | main thread Painter; canvas/font/layout을 제공. |
| ads | 없음 | 두 슬롯 public AdView mapping. |
| authenticated | 없음 | 로그인 완료이며 로그아웃 중이 아닌지 bool. |

반환·실패: 성공 슬롯→decision ID dict; decode 실패 슬롯은 제외.

의사코드: 카드/refresh 안내 → ready선택 image decode → 성공 title/body/금액/ID 일치 표시 → receipt 추가.

직접 호출: `ads.items`, `self.images.clear`, `painter.card`, `painter.button`, `painter.text`, `painter.wrapped`, `self.image`, `painter.canvas.blit`, `pygame.Rect`, `pygame.transform.scale`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.
