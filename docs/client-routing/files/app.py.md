# app.py

## 계층과 책임

앱 제어 — Pygame 입력을 요청 큐에 넣고 결과를 state와 패널로 전달한다. HTTP·WS 내부나 서버 규칙을 구현하지 않는다.

원문: `Game-client/app.py`. 호출 경계는 아래 직접 의존성까지만 기술합니다.

## 직접 의존성

```text
from network import NetworkWorker
from render import Renderer
from state import VillageState
import pygame
import queue
```

## 변수·상수와 출처

인스턴스/지역 변수는 각 함수 의사코드의 설정식이 출처입니다. 필드 갱신은 해당 메서드 항목에만 기록합니다.

```text
없음
```

## run(config)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `config`: configuration.load_config()가 읽은 설정 dict.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 network ← NetworkWorker(config)
실행 pygame.display.init()
실행 pygame.font.init()
실행 pygame.display.set_caption('작은 마을 · Game-client')
설정 screen ← pygame.display.set_mode((config['window_width'], config['window_height']), pygame.RESIZABLE)
설정 renderer ← Renderer(screen, config)
설정 state ← VillageState()
설정 clock ← pygame.time.Clock()
설정 (username, password, focus) ← ('', '', 'username')
실행 pygame.key.start_text_input()
설정 closing ← False
실행 network.start()
내부 함수 action 정의 → 아래 별도 시그니처 문서 참조
내부 함수 login 정의 → 아래 별도 시그니처 문서 참조
시도:
  반복 True:
    반복 _ ← range(200):
      시도:
        설정 event ← network.events.get_nowait()
      예외 queue.Empty:
        반복 종료
      실행 state.accept(event)
      반복 panel ← renderer.query_panels.values():
        실행 panel.accept(event, state)
      조건 event.get('kind') == 'delivery' and state.delivery 이면:
        설정 state.message ← state.delivery['message']
      조건 event['kind'] in ('logged_out', 'stopped') 이면:
        설정 username, password ← ''
    반복 event ← pygame.event.get():
      조건 event.type == pygame.QUIT 이면:
        설정 closing ← True
        설정 password, username ← ''
        실행 network.stop()
      조건 closing 이면:
        다음 반복으로
      조건 event.type == pygame.VIDEORESIZE 이면:
        설정 screen ← pygame.display.set_mode((max(320, event.w), max(240, event.h)), pygame.RESIZABLE)
        설정 renderer.screen ← screen
      그 외:
        조건 event.type == pygame.TEXTINPUT and focus and (state.phase == 'signed_out') 이면:
          설정 value ← ''.join((c for c in event.text if c.isprintable()))
          조건 focus == 'username' 이면:
            설정 username ← (username + value)[:150]
          그 외:
            설정 password ← (password + value)[:256]
        그 외:
          조건 event.type == pygame.KEYDOWN 이면:
            조건 focus 이면:
              조건 event.key == pygame.K_TAB 이면:
                설정 focus ← 'password' if focus == 'username' else 'username'
              그 외:
                조건 event.key == pygame.K_ESCAPE 이면:
                  설정 focus ← None
                  실행 pygame.key.stop_text_input()
                그 외:
                  조건 event.key == pygame.K_BACKSPACE 이면:
                    조건 focus == 'username' 이면:
                      설정 username ← username[:-1]
                    그 외:
                      설정 password ← password[:-1]
                  그 외:
                    조건 event.key == pygame.K_RETURN 이면:
                      실행 login()
              다음 반복으로
            설정 directions ← {pygame.K_UP: 'up', pygame.K_DOWN: 'down', pygame.K_LEFT: 'left', pygame.K_RIGHT: 'right', pygame.K_SPACE: 'gather', pygame.K_x: 'train'}
            조건 event.key in directions 이면:
              실행 action(directions[event.key])
            그 외:
              조건 event.key == pygame.K_TAB and state.phase == 'signed_out' 이면:
                설정 focus ← 'username'
                실행 pygame.key.start_text_input()
          그 외:
            조건 event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 이면:
              설정 hit ← renderer.hit_test(event.pos)
              조건 hit in ('username', 'password') 이면:
                설정 focus ← hit
                실행 pygame.key.start_text_input()
                다음 반복으로
              설정 focus ← None
              실행 pygame.key.stop_text_input()
              조건 hit == 'login' 이면:
                실행 login()
              그 외:
                조건 hit == 'logout' and state.own is not None and (state.phase != 'logging_out') 이면:
                  조건 network.submit({'kind': 'logout'}) 이면:
                    설정 state.phase ← 'logging_out'
                    설정 state.message ← '로그아웃 확인 중…'
                    설정 password ← ''
                그 외:
                  조건 hit == 'delivery' 이면:
                    설정 request ← state.request_delivery()
                    조건 request is not None and (not network.submit(request)) 이면:
                      설정 state.delivery_busy ← False
                      설정 state.delivery_sent_at ← float('-inf')
                  그 외:
                    조건 hit == 'delivery_api' 이면:
                      설정 state.show_delivery_api ← not state.show_delivery_api
                    그 외:
                      조건 hit in renderer.query_panels or hit == 'actions_refresh' 이면:
                        설정 kind ← 'actions' if hit == 'actions_refresh' else hit
                        설정 panel ← renderer.query_panels[kind]
                        설정 request ← panel.request(state)
                        조건 request is not None 이면:
                          반복 other ← renderer.query_panels.values():
                            조건 other is not panel 이면:
                              설정 other.opened ← False
                          설정 renderer.api_source ← kind
                          설정 renderer.api_scroll ← 0
                          조건 not network.submit(request) 이면:
                            실행 panel.reset()
                            설정 state.message ← '요청 큐가 가득 찼어요. 다시 눌러 주세요.'
                      그 외:
                        조건 hit and '_' in hit and (hit.rsplit('_', 1)[0] in renderer.query_panels) 이면:
                          설정 (kind, operation) ← hit.rsplit('_', 1)
                          설정 panel ← renderer.query_panels[kind]
                          조건 operation == 'close' 이면:
                            설정 panel.opened ← False
                          그 외:
                            조건 operation in ('previous', 'next') 이면:
                              실행 panel.turn_page(-1 if operation == 'previous' else 1)
                        그 외:
                          조건 hit == 'api_source' and state.show_delivery_api 이면:
                            설정 sources ← ('delivery', *renderer.query_panels)
                            설정 renderer.api_source ← sources[(sources.index(renderer.api_source) + 1) % len(sources)]
                            설정 renderer.api_scroll ← 0
                          그 외:
                            조건 hit in ('api_up', 'api_down') and state.show_delivery_api 이면:
                              설정 renderer.api_scroll ← max(0, renderer.api_scroll + (-3 if hit == 'api_up' else 3))
                            그 외:
                              조건 hit in ('up', 'down', 'left', 'right', 'gather', 'train') 이면:
                                실행 action(hit)
    실행 renderer.draw(state, username, password, focus, clock.get_fps(), closing=closing)
    조건 not network.thread.is_alive() 이면:
      반복 종료
    실행 clock.tick(config['fps'])
항상 정리:
  설정 password, username ← ''
  실행 network.stop()
  반복 network.thread.is_alive():
    실행 pygame.event.pump()
    실행 renderer.draw(state, '', '', None, clock.get_fps(), closing=True)
    실행 clock.tick(config['fps'])
  실행 network.thread.join(timeout=0)
  실행 pygame.quit()
반환 0
```

직접 호출 (내부 구현을 펼치지 않음):

```text
''.join
NetworkWorker
Renderer
VillageState
action
c.isprintable
clock.get_fps
clock.tick
event.get
float
hit.rsplit
len
login
max
network.events.get_nowait
network.start
network.stop
network.submit
network.thread.is_alive
network.thread.join
panel.accept
panel.request
panel.reset
panel.turn_page
pygame.display.init
pygame.display.set_caption
pygame.display.set_mode
pygame.event.get
pygame.event.pump
pygame.font.init
pygame.key.start_text_input
pygame.key.stop_text_input
pygame.quit
pygame.time.Clock
range
renderer.draw
renderer.hit_test
renderer.query_panels.values
sources.index
state.accept
state.request_delivery
```

## run.action(name)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `name`: 호출자가 전달하는 `name`; 값의 사용과 직접 호출 출처는 아래 의사코드에 표시.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 request ← state.command(name if name in ('gather', 'train') else 'move', name)
조건 request is not None and (not network.submit(request)) 이면:
  실행 state.accept({'kind': 'status', 'phase': 'disconnected', 'message': '요청 큐가 가득 찼어요. 로그아웃 후 다시 시도하세요.'})
```

직접 호출 (내부 구현을 펼치지 않음):

```text
network.submit
state.accept
state.command
```

## run.login()

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- 없음.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
nonlocal password, focus
조건 state.phase != 'signed_out' or not username.strip() or (not password) 이면:
  설정 state.message ← '아이디와 비밀번호를 모두 입력해 주세요.'
  반환 None
설정 accepted ← network.submit({'kind': 'login', 'username': username.strip(), 'password': password})
설정 password ← ''
조건 accepted 이면:
  반복 panel ← renderer.query_panels.values():
    실행 panel.reset()
  실행 state.clear_account()
  설정 state.phase ← 'authenticating'
  설정 state.message ← '로그인 확인 중…'
  설정 focus ← None
  실행 pygame.key.stop_text_input()
```

직접 호출 (내부 구현을 펼치지 않음):

```text
network.submit
panel.reset
pygame.key.stop_text_input
renderer.query_panels.values
state.clear_account
username.strip
```
