# client/contracts/history.py

## 책임

현재 player의 최근 행동 이력에서 표시 허용 필드만 복사한다.

## 함수

`read_history(data, player_id)`

```text
scope=current-player, limit=20, 최대 20 events 검사
각 event 소유자·UUID·schema·시간·상태 필드 검사
선택 transition의 step/reward/flag/manual-v1/action/observation 검사
비밀번호·쿠키·토큰을 제외한 새 dict 반환
```

`data`는 `/api/history/` object JSON, `player_id`는 AuthSession의 Identity에서 온다. 직접 호출: `UUID`, `datetime.fromisoformat`.
