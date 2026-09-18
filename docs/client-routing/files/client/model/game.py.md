# client/model/game.py

## 책임과 상태 출처

서버가 확정한 내 상태·방 구성원·명령 대기·epoch만 소유한다. wire dict는 `contracts.game`으로 검증하며 UI·HTTP를 호출하지 않는다.

## 메서드

`GameState.ready(self)` — connected, own, 첫 WS state가 모두 있을 때 True인 property다.

`GameState.online_label(self)` — snapshot 수와 epoch로 온라인/마지막 정보 문구를 반환한다.

`GameState.command(self, action, direction=None, *, now=None)`

```text
ready·pending·0.2초 제한·행동과 수련 위치 검사
uuid.uuid4 command_id 생성
로컬 좌표/보상은 변경하지 않고 queue request만 반환
```

`GameState.cancel_submission(self)` — queue 실패한 pending과 행동을 지운다.

`GameState.clear(self)` — 계정·방·pending·snapshot·clock 상태를 초기화한다.

`GameState.apply_status(self, phase, epoch)` — 연결 상태와 epoch를 기록하고 끊긴 pending을 abandoned로 이동한다.

`GameState.apply_identity(self, data)` — `read_state` 결과를 own과 players에 기록한다.

`GameState.apply_snapshot(self, data, epoch)` — 같은 epoch·room 구성원만 병합하고 player별 높은 version을 보존한다.

`GameState.apply_state(self, data, epoch, first=False)`

```text
epoch·room·version 검사
타인 state는 타인 player만 갱신
내 state는 matching command_id일 때만 pending 완료
수련 응답은 matching command_id 전까지 coins를 확정하지 않음
결과 메타데이터 반환
```

`GameState.apply_error(self, command_id)` — 일치하는 pending만 종료한다.

직접 호출: `read_state`, `read_snapshot`, `time.monotonic`, `uuid.uuid4`.
