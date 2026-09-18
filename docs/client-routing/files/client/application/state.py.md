# client/application/state.py

## 책임과 상태 출처

Pygame 타입 없이 입력 초안·화면 상태와 renderer용 불변 표시 DTO를 정의한다. mutable 값은 Controller만 쓴다.

## 타입과 변수

```text
LoginDraft: username='', password='', focus='username'
ApplicationState: phase='signed_out', message, closing/stopped, API 화면과 최근 WS 문구
LoginView/ApplicationView/GameView/QueryView/ScreenModel: Controller가 프레임마다 복사해 만드는 frozen DTO; QueryView.can_request는 busy와 최소 간격에서 계산
```

## 메서드

`LoginDraft.clear(self)`

```text
username·password를 빈 문자열로 만들고 focus를 None으로 설정
```

`ApplicationState.remember_ws(self, message)`

```text
message를 추가하고 최근 3개만 유지
```

`ApplicationState.clear_account(self)`

```text
LoginDraft.clear 호출
API 표시·scroll·최근 WS 목록 초기화
```

파라미터 값은 Controller의 intent/event에서 온다. 외부 서비스 호출은 없다.
