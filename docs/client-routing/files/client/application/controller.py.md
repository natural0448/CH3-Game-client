# client/application/controller.py

## 책임과 직접 의존성

사용자 intent와 network event를 유일한 상태 쓰기 소유자에게 전달한다. 구체 worker 대신 `NetworkPort`를 받고 `GameState`, `QueryStore`, `ApplicationState`를 조정한다.

## 메서드

`Controller.__init__(self, network: NetworkPort)` — port와 세 상태 객체를 저장한다.

`Controller.screen_model(self)`

```text
ApplicationState·GameState·QueryStore를 복사
비밀번호 문자열 대신 길이만 LoginView에 기록
조회 page·filter_value를 포함한 frozen ScreenModel 반환
```

`Controller.login(self)` — 입력 검사 → password 지역 요청 생성 → port.submit → 상태·조회 초기화; 제출 후 password를 비운다.

`Controller.logout(self)` — 계정과 phase를 확인해 `{kind: logout}`을 제출하고 logging_out을 기록한다.

`Controller.command(self, name)` — `GameState.command` 결과만 제출하며 queue 실패 시 pending을 취소한다.

`Controller.request_query(self, kind)` — 계정·phase 검사 → `QueryStore.request` → port 제출; GET 종류만 생성한다.

`Controller.handle_intent(self, intent)`

```text
quit/focus/text/login/logout/command/query/panel page/filter/API 의도를 구분
panel_filter는 QueryStore.set_filter에만 전달하여 새 GET을 만들지 않음
해당 공개 메서드 또는 상태 소유자만 호출
Pygame·aiohttp를 호출하지 않음
```

`Controller.handle_network_event(self, event)`

```text
status/identity/state/snapshot/error는 GameState에 전달
조회 결과는 QueryStore.accept에 전달
로그인 종료·worker 종료는 계정 상태를 초기화
표시 문구와 최근 WS 요약만 ApplicationState에 기록
```

파라미터는 InputRouter 또는 worker queue에서 온 credential-free dict다. 직접 호출: `NetworkPort.submit/stop`, `GameState`, `QueryStore`, `copy.deepcopy`.
