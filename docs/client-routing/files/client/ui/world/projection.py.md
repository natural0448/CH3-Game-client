# client/ui/world/projection.py

## 책임과 DTO

서버 확정 player iterable을 Pygame 없는 frozen 표시 DTO로 바꾼다. `ActorView`는 id/tile/pixel/mine, `NameplateView`는 tile과 label을 가진다.

## 함수

`project_players(players, own_player_id)`

```text
y/mine/player_id로 안정 정렬
tile을 32px world 좌표로 변환
같은 tile 구성원을 그룹화
username 또는 #player_id label, 인원 suffix 생성
(actors, nameplates) 반환
```

직접 호출: `sorted`, dataclass 생성. GameState와 Pygame을 호출하지 않는다.
