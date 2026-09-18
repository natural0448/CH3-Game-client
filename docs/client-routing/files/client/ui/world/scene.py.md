# client/ui/world/scene.py

## 책임

마을 layer의 호출 순서만 조립한다.

## 함수

`draw_world(painter, game, layout)`

```text
world card
terrain → decorations → markers
확정 state가 있으면 project_players → actors → nameplates
```

직접 호출: `draw_terrain`, `draw_decorations`, `draw_markers`, `project_players`, `draw_actors`, `draw_nameplates`.
