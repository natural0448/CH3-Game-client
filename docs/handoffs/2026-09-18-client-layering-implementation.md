# Game-client 계층화 구현 인수인계

작성일: 2026-09-18

## 완료 범위

`docs/client-routing/layering-plan.md`의 최종 설계를 전체 클라이언트에 적용했다. 서버·API 계약·인증 정책·Kafka·Spark는 수정하지 않았다.

## 계층별 소유권

- `client/application`: 사용자 intent, query request_id, 화면 문구와 frozen `ScreenModel`
- `client/model`: 서버 확정 player/room/x/y/coins/version, player별 version, command_id, epoch
- `client/contracts`: auth, game state/snapshot, history, delivery/analytics/actions allowlist
- `client/network`: 단일 worker 안의 HTTP session, WS play, GET query 작업
- `client/ui`: 동일 Layout을 쓰는 input/render, section, panel, world layer

## 실행과 확인

```powershell
cd C:\MLO01-01\Chapter3\Game-client
.\.venv\Scripts\python.exe client\main.py --check
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py" -v
.\.venv\Scripts\python.exe tools\check_routing_docs.py
.\.venv\Scripts\python.exe client\main.py
```

처음 세 명령은 서버 없이 실행할 수 있다. 마지막 명령의 로그인·WebSocket 확인에는 기존 Game-server가 필요하다.

## Git 구분

기준은 `a3d0a59 client-commit`의 깨끗한 작업 트리다. 기존 root 구현·테스트와 해당 문서는 삭제 상태이며, 새 `client/`, `tests/`, 1:1 문서는 untracked 상태다. staged 변경은 없고 commit하지 않았다. 상세 목록과 검사 결과는 `docs/client-routing/verification/2026-09-18-layering.md`에 기록했다.

## 남은 확인

실제 서버 환경에서 두 계정 로그인, 첫 state, 같은 방 snapshot, 이동·채집·X수련, 행동 통계 버튼, disconnect 3회 재연결, 로그아웃 순서와 창 종료를 확인한다. 클라이언트는 이번 작업 중 어떤 서비스도 시작하지 않았다.
