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
network나 상태 쓰기 메서드는 호출하지 않음
```

`event`는 메인 스레드 Pygame event, `app/queries`는 현재 입력과 열린 패널 상태다. 직접 호출: `Layout.hit_test`, 문자열 분리 메서드.
