# client/ui/sections/account.py

## 책임

로그인 입력과 입장 버튼을 표시한다. password 문자열을 받지 않고 `LoginView.password_length`만큼 bullet을 그린다.

## 함수

`draw_account(painter, app)` — username/password Rect, focus 테두리, 로그인 버튼, 키 안내를 그린다.

직접 호출: `Painter.card/text/button`, `pygame.draw.rect`, Surface clip.
