# client/ui/drawing.py

## 책임과 상수

색상과 작은 Pygame primitive를 소유한다. `INK/MUTED/GREEN/CREAM/WHITE/LINE`은 화면 표현값이며 게임 규칙이 아니다.

## 메서드

`Painter.__init__(self, canvas, assets, layout)` — 현재 frame의 Surface, font/image cache, Layout을 참조한다.

`Painter.text(self, text, position, size=17, color=INK)` — 지정 font를 render해 blit한다.

`Painter.wrapped(self, text, rect, size=15, color=MUTED)` — 글자 폭으로 줄바꿈하고 Rect 바깥은 그리지 않는다.

`Painter.card(self, rect, color=WHITE)` — 둥근 배경과 LINE 테두리를 그린다.

`Painter.button(self, name, label, enabled=True)` — Layout control Rect에 활성/비활성 버튼을 그린다.

직접 호출: Pygame font, Surface.blit, draw.rect.
