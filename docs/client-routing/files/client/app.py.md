# client/app.py

메인 스레드에서 worker 결과/입력/프레임을 처리한다. run은 활성 창에서 tick_ads를 수행하고 ScreenRenderer.render의 flip 이후 receipt·AdsRenderer.failures를 Controller.confirm_ad_display에 전달한다. HTTP는 worker 스레드가 실행한다. GUI 종료에는 기존 stop/drain/join/pygame.quit을 유지한다. config는 configuration.load_config의 기존 값이다.

직접 호출 기대 계약: UI/상태 helper는 각 짝 문서의 반환 계약을 따른다. worker.submit은접수bool, HTTP/JSON helper는공개dict 또는공개오류, read_ad_event는id/type/created dict, emit은queue전달, create_task는Task, Pygame draw/decode는Surface/표시receipt, fixture Web은bytes이다. 하위 계층 내부를 복제하지 않는다.

## `_sync_text_input(focus)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| focus | 없음 | 해당함수/fixture에 전달되는공개입력. 실제호출범위에서검사한다. |

반환·실패: None.

의사코드: focus에따라SDL text input start/stop.

직접 호출: `pygame.key.start_text_input`, `pygame.key.stop_text_input`.

## `run(config)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| config | 없음 | 현재configuration의창/연결설정dict. |

반환·실패: 정상0.

의사코드: worker/SDL 초기화 → 결과/입력/활성창tick/렌더/receipt → 종료때drain/join/quit.

직접 호출: `Controller`, `InputRouter`, `NetworkWorker`, `ScreenRenderer`, `_sync_text_input`, `build_layout`, `clock.get_fps`, `clock.tick`, `controller.app.login.clear`, `controller.confirm_ad_display`, `controller.handle_intent`, `controller.handle_network_event`, `controller.screen_model`, `controller.tick_ads`, `input_router.route`, `network.drain_events`, `network.is_alive`, `network.start`, `network.stop`, `pygame.display.get_active`, `pygame.display.init`, `pygame.display.set_caption`, `pygame.display.set_mode`, `pygame.event.get`, `pygame.event.pump`, `pygame.font.init`, `pygame.quit`, `pygame.time.Clock`, `renderer.render`, `renderer.set_screen`, `screen.get_size`.

## 상태·값 출처

지역 변수는 입력·기존 설정·검증한 공개응답·monotonic시간 또는 자기fixture에서 얻으며 해당함수/클래스가 쓴다. 전역/타이머/큐/fixture의 주요 초기값과 쓰기 소유자는 위 파일설명에 기록한다. 실제env값·계정암호·cookie·CSRF토큰은기록하지않는다.
