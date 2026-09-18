# 작은 마을 접속기

```powershell
cd C:\MLO01-01\Chapter3\Game-client
.\.venv\Scripts\python.exe main.py
```

Python 3.12 전용 가상환경과 requirements.txt의 패키지가 설치되어 있습니다. 설정만 확인하려면 `main.py --check`를 사용합니다.

먼저 Game-server의 Django 서버를 실행해야 로그인할 수 있습니다. config.json의 server_base_url은 http://127.0.0.1:8000입니다. JSON 인증 API와 WS가 준비되어 있습니다. 브라우저 로그인 쿠키를 복사하지 않습니다.

방향키/방향 버튼으로 이동하고, Space/채집 버튼으로 (2,2)에서 채집합니다. 로그인 입력 필드에 포커스가 있으면 방향키를 보내지 않습니다. Esc 또는 화면의 빈 곳을 클릭하면 입력 포커스를 해제합니다.

게임 상태는 서버 응답 이후에만 바뀝니다. 연결이 끊기면 조작을 중지하고 worker가 2초 간격으로 최대 3회 재연결합니다. 전송 중이던 명령은 자동 재전송하지 않습니다. 로그아웃 버튼은 WS를 닫고 서버 로그아웃 후 로컬 상태를 지웁니다.

11일차 6교시까지 반영했습니다. snapshot의 전체 접속자 목록과 각 player_id의 state를 표시합니다. 다른 사람의 이동은 내 좌표·동전·명령 대기·오류 안내를 바꾸지 않습니다. 퇴장한 사람은 다음 snapshot에서 제거합니다. 캐릭터 위에는 로그인 아이디를 표시하며, 같은 좌표에 겹친 경우에는 이름 목록과 인원수를 표시합니다.

상단에서 방 이름·온라인 인원·내 위치·동전·연결 상태를 확인하세요. 인원은 최신 snapshot 기준이며, 연결이 끊기거나 재연결 후 새 snapshot을 기다리는 동안에는 마지막 인원과 `마지막 정보`를 표시합니다. 오른쪽에는 방 접속 현황과 최근 WS 메시지 요약 3개를 표시합니다. 로그인에 필요한 내부 `/api/player/` 요청은 유지합니다.

클라이언트 파일을 수정한 뒤에는 두 게임 창을 모두 닫고 다시 실행해야 변경 사항이 적용됩니다. 서로 다른 계정으로 로그인해야 하며, 같은 계정의 두 번째 연결은 서버가 거절합니다.

`assets/README.md`에 원본 PNG/폰트와 라이선스를 기록했습니다. 모든 경로는 config.json 위치를 기준으로 읽습니다.

6교시 계약·확인 절차: `../Game-server/data/notes/day11-client-prompt.md`.

대기·통계 패널의 **내 이벤트 전달 상태**를 누르면 같은 로그인 세션으로 `GET /api/delivery/`를 한 번 조회합니다. 재조회는 최소 5초 간격이며 자동 조회하지 않습니다. 내 이벤트 수·미발행 수와 `source: mysql-outbox`를 표시합니다. 이는 MySQL outbox의 조회 시점 정보이며 Spark 집계가 아닙니다. 조회 중에도 이동 요청과 WS 수신은 계속 처리됩니다.

오른쪽 **API 응답 보기**는 전달 상태·Spark 통계·내 이력의 GET 경로·status·허용된 JSON 필드만 보여 줍니다. 패널 상단의 응답 종류 버튼으로 전환하고 화살표로 스크롤합니다. **WS 메시지 보기**로 되돌릴 수 있습니다. 302/401은 로그인 안내로 처리하며 HTML·인증 응답·쿠키·CSRF·비밀번호는 표시하지 않습니다.

오프라인 확인: `.\.venv\Scripts\python.exe -m unittest test_multiplayer test_delivery_client -v`.

## 13일차 7교시 · 기존 python 계정으로 개인 수련

서버 터미널에서 실행 중인 Django를 Ctrl+C로 종료하고 다시 시작합니다.

```powershell
cd C:\MLO01-01\Chapter3\Game-server\server
.\.venv\Scripts\python.exe manage.py runserver --noreload 127.0.0.1:8000
```

게임 창도 닫고 다른 터미널에서 다시 실행합니다.

```powershell
cd C:\MLO01-01\Chapter3\Game-client
.\.venv\Scripts\python.exe main.py
```

1. 기존 `python` 아이디와 직접 설정한 비밀번호로 로그인합니다. 별도 `day13_train` 계정은 필요하지 않습니다.
2. 화면에 표시된 내 좌표를 보고 `(3, 2)`로 이동합니다. `(6, 2)`라면 왼쪽으로 세 번입니다. 로그인 입력에 포커스가 남아 있으면 Esc를 먼저 누릅니다.
3. **X키** 또는 **수련 [X] · (3, 2)** 버튼을 한 번 누릅니다. 연결·좌표·첫 state·미완료 명령 조건을 만족해야 동작합니다. 로그인 입력에 포커스가 있으면 X키는 글자 입력으로 처리합니다. 서버가 확정하면 coins와 version이 1 증가하고 **수련 완료 · 동전 1 획득**을 표시합니다.
4. 수련 후에도 게임 화면을 유지합니다. **내 이력 읽기** 버튼을 누를 때만 이력을 조회하고 창을 엽니다. 최신 `player.trained`, `reward 1`, `action train`, event_id를 확인하세요. 자동 수련은 없습니다.
5. **내 이력 읽기**로 최근 20개까지 다시 조회합니다. event_type·지역 시각·step·reward·action.type·event_id를 표시합니다. 4개씩 이전/다음 페이지로 넘깁니다. 이력이 없으면 안내하고, transition이 없는 행은 **확장 이전 기록** 및 **action 기록 없음**으로 표시합니다.
6. **API 응답 보기 → 내 이력 응답**에서 같은 event_id의 observation/next_observation을 비교합니다. 두 coins 값의 차이가 reward입니다. 서버 `GET /api/history/`는 로그인한 계정만 조회하며 다른 player_id 쿼리는 조회 범위를 바꾸지 않습니다.

기존 python 계정의 이전 행동을 삭제하거나 좌표를 초기화하지 않습니다. 확장 이후 성공한 move/gather/train 다섯 개가 한 묶음이며, 다섯 번째만 done/truncated가 true입니다. 현재 묶음 진행도에 따라 첫 수련의 step이 반드시 1인 것은 아닙니다. 전체 이력 분석과 8교시 전이 파일 내보내기는 최근 20개 화면 조회와 별개입니다.

변경 파일: Game-server의 `server/game/views.py`, `urls.py`; Game-client의 `network.py`, `state.py`, `main.py`, `render.py`, `panels.py`, `history_data.py`. 검증은 서버 `game.test_history`와 클라이언트 `test_history_client`에 추가했습니다.

```powershell
.\.venv\Scripts\python.exe -m unittest test_history_client test_multiplayer test_delivery_client -v
```
