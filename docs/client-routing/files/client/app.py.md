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
