# client/ui/renderer.py

## 책임과 상태

메인 스레드 화면 합성과 마지막 display 반영만 맡는다. `screen`, logical `canvas`, `AssetStore`를 소유하며 game/query/application 상태를 쓰지 않는다.

## 메서드

`ScreenRenderer.__init__(self, screen, config)` — main thread를 확인하고 CANVAS Surface와 AssetStore를 만든다.

`ScreenRenderer.set_screen(self, screen)` — resize로 바뀐 display Surface만 교체한다.

`ScreenRenderer.render(self, model, layout, fps)`

```text
ScreenModel에서 frozen app/game/query view 읽기
header → account → world → commands → activity → lobby
connection overlay → query overlay → bottom status 순서로 호출
Layout.viewport로 scale/letterbox 후 pygame.display.flip
```

직접 호출: section/world/panel/overlay 함수, `Painter`, Pygame Surface/transform/display.

## 22일차 이미지 광고 최종 반영

ScreenRenderer는 AdsRenderer를 소유하고 lobby 다음 광고 카드, 이후 overlay/status 순서로 그린다. render는 pygame.display.flip이 성공한 active display일 때 slot→decision ID receipt를 반환한다. inactive display는 빈 dict. 이미지 decode 실패 슬롯에는 receipt가 없고 상태 쓰기는 caller가 수행한다.

클래스 계약: `class ScreenRenderer`.


### `ScreenRenderer.__init__(self, screen, config)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |
| screen | 없음 | Pygame display Surface. |
| config | 없음 | load_config의 공개 설정 dict; 계정/매체키 없음. |

반환·실패: None.

의사코드: 해당 파일 책임에 정의한 소유 상태/fixture를 초기화·정리 또는 교체.

직접 호출: `pygame.Surface`, `AssetStore`, `AdsRenderer`, `threading.current_thread`, `threading.main_thread`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `ScreenRenderer.set_screen(self, screen)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |
| screen | 없음 | Pygame display Surface. |

반환·실패: None.

의사코드: 기존 입력·상태 검사 → 직접 호출 → 현재 결과/상태 전달; 이미지 추가 책임은 위 파일 설명 참조.

직접 호출: 없음. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `ScreenRenderer.render(self, model, layout, fps)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |
| model | 없음 | frozen ScreenModel. |
| layout | 없음 | 동일 draw/hit-test Layout. |
| fps | 없음 | 현재 frame rate 숫자. |

반환·실패: active 성공 display에서 dict[str,str], inactive이면 {}.

의사코드: 기존 section/world → AdsRenderer.draw → overlay/status → viewport → display.flip → active receipt.

직접 호출: `Painter`, `self.canvas.fill`, `draw_header`, `draw_account`, `painter.button`, `draw_world`, `draw_commands`, `draw_activity`, `draw_lobby`, `self.ads.draw`, `draw_connection_overlay`, `draw_query_panels`, `draw_status`, `layout.viewport`, `self.screen.fill`, `self.screen.blit`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.
