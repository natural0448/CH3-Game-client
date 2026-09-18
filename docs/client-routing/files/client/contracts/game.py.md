# client/contracts/game.py

## 책임과 상수

게임 wire allowlist다. `WIDTH=20`, `HEIGHT=15`, `TILE=32`, `GATHER_TILE=(2,2)`, `TRAIN_TILE=(3,2)`이며 오류 문구는 고정 `ERROR_MESSAGES`에서 온다.

## 함수

`read_state(data)`

```text
type='state'와 player_id/room_id/x/y/coins/version 타입·범위 검사
username은 150자 이하 표시 메타데이터만 허용
새 dict 반환
```

`read_snapshot(data)` — 최대 20개 players를 각각 `read_state`로 검증해 player_id key dict로 반환한다.

`read_command_id(data)` — 1..64 문자열 command_id만 반환하고 아니면 None이다.

외부 호출은 없다.
