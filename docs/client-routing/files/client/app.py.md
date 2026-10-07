# client/app.py

## 책임과 직접 의존성

메인 스레드에서 객체를 조립하고 프레임·종료 수명만 관리한다. `Controller`, `NetworkWorker`, `InputRouter`, `Layout`, `ScreenRenderer`를 직접 연결한다.

## 함수

`_sync_text_input(focus)`

```text
focus가 있으면 pygame.key.start_text_input
없으면 pygame.key.stop_text_input
```

`run(config)`

```text
config로 worker·창·renderer·controller 생성
worker 한 개 시작
매 프레임 drain_events → Controller.handle_network_event
같은 Layout으로 InputRouter.route와 ScreenRenderer.render 호출
resize는 display와 Layout만 교체
종료 시 worker.stop → task/session/thread 종료를 기다림 → pygame.quit
0 반환
```

`config`는 `config.json`에서 검증된 dict다. 직접 호출: Pygame display/event/clock, `NetworkPort` 구현, `Controller`, `build_layout`, `ScreenRenderer`.

## 22일차 이미지 광고 최종 반영

기존 main-thread frame loop는 controller.tick_ads로 최초 준비 슬롯만 요청한다. ScreenRenderer.render가 flip 이후 반환한 receipt mapping만 AdStore.mark_displayed에 전달한다. 네트워크/게임 이동/종료 흐름은 유지한다. 종료 렌더는 기록하지 않는다. 노출 API 호출 없음.

### `_sync_text_input(focus)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| focus | 없음 | 기존 focus 입력; 아래 동작·직접 호출과 기존 계약 참조. |

반환·실패: None.

의사코드: 기존 입력·상태 검사 → 직접 호출 → 현재 결과/상태 전달; 이미지 추가 책임은 위 파일 설명 참조.

직접 호출: `pygame.key.start_text_input`, `pygame.key.stop_text_input`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.

### `run(config)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| config | 없음 | load_config의 공개 설정 dict; 계정/매체키 없음. |

반환·실패: 코드 반환 식: `0`.

의사코드: 기존 입력·상태 검사 → 직접 호출 → 현재 결과/상태 전달; 이미지 추가 책임은 위 파일 설명 참조.

직접 호출: `NetworkWorker`, `Controller`, `pygame.display.init`, `pygame.font.init`, `pygame.display.set_caption`, `pygame.display.set_mode`, `ScreenRenderer`, `InputRouter`, `pygame.time.Clock`, `_sync_text_input`, `network.start`, `controller.app.login.clear`, `network.stop`, `network.is_alive`, `pygame.quit`, `network.drain_events`. 호출 결과는 이 함수의 반환·상태 갱신에 사용한다. 외부 계층의 내부 구현은 그 계층 문서에서 설명한다.
