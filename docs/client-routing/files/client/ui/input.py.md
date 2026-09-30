# client/ui/input.py

## 책임과 상수

Pygame event를 credential-free application intent로 변환한다. `GAME_KEYS`는 방향키, Space 채집, X 수련이다.

## 메서드

`InputRouter.route(self, event, layout, app, queries)`

```text
QUIT/resize/text/key/mouse를 구분
로그인 focus 중 game key를 반환하지 않음
mouse는 같은 frame Layout.hit_test 사용
login/logout/command/query/panel/API intent dict 반환
windows 진입과 windows_refresh는 같은 query intent로 변환
analytics 진입과 analytics_refresh는 같은 analytics query intent로 변환
load/metrics 진입과 각 refresh는 같은 이름의 query intent로 변환
lake 진입과 lake_refresh는 {kind:query, query:lake}로 변환
lake_close는 기존 suffix 규칙에 따라 panel_close intent로 변환
windows_filter_all/tumbling/sliding은 network query가 아닌 panel_filter intent로 변환
network나 상태 쓰기 메서드는 호출하지 않음
```

`event`는 메인 스레드 Pygame event, `app/queries`는 현재 입력과 열린 패널 상태다. 직접 호출: `Layout.hit_test`, 문자열 분리 메서드.
