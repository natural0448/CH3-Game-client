# client/ui/renderer.py

## 책임과 상태

메인 스레드 화면 합성과 마지막 display 반영만 맡는다. `screen`, logical `canvas`, `AssetStore`를 소유하며 game/query/application 상태를 쓰지 않는다.

## 메서드

`ScreenRenderer.__init__(self, screen, config)` — main thread를 확인하고 CANVAS Surface와 AssetStore를 만든다.

`ScreenRenderer.set_screen(self, screen)` — resize로 바뀐 display Surface만 교체한다.

`ScreenRenderer.render(self, model, layout, fps)`

```text
ScreenModel에서 frozen app/game/query view 읽기
header → account → world → commands → activity → lobby
connection overlay → query overlay → bottom status 순서로 호출
Layout.viewport로 scale/letterbox 후 pygame.display.flip
```

직접 호출: section/world/panel/overlay 함수, `Painter`, Pygame Surface/transform/display.
