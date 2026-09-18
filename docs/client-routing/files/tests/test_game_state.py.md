# tests/test_game_state.py

## 책임

서버 확정 상태의 방·version·epoch·command_id 경계를 검사한다.

## 메서드

`GameStateTests.setUp(self)` — player 1의 identity/epoch/첫 state를 만든다.

`GameStateTests.test_other_players_and_snapshot_never_ack_my_command(self)` — 타인 state/snapshot이 내 pending을 끝내거나 own 좌표를 바꾸지 않는지 검사한다.

`GameStateTests.test_room_version_epoch_disconnect_and_no_replay(self)` — 타 방 제외, 높은 version 보존, disconnect pending abandoned를 검사한다.

`GameStateTests.test_training_requires_tile_and_matching_ack(self)` — 수련 tile과 matching command_id 뒤에만 coins가 확정되는지 검사한다.

직접 호출: `GameState` 공개 메서드와 `tests.support.player`.
