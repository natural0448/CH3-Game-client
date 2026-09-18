# client/ui/sections/header.py

## 책임과 상수

제목, 방·온라인·내 위치·coins, 네트워크 phase, FPS를 그린다. `PHASES`는 ApplicationView phase의 한글 표시 map이다.

## 함수

`draw_header(painter, app, game, fps)` — frozen view 값을 한 줄로 render하고 905px을 넘으면 비율 scale한다.

직접 호출: `Painter.text`, font render, `pygame.transform.smoothscale`.
