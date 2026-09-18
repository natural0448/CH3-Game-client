# 14일차 7교시 확인 기록

## 변경 범위

작업 루트는 `C:/MLO01-01/Chapter3/Game-client`입니다. 이 폴더에 기존 라우팅 문서와 Git 저장소가 없었습니다. 전체 저장소 탐색 대신 클라이언트의 개발 파일 목록과 필요한 코드, 기존 행동 API의 view·경로·완료된 집계 파일만 확인했습니다. 서버·API·게임 규칙·DB·Kafka 데이터는 수정하지 않았습니다.

수정한 개발 파일 5개: README.md, main.py, network.py, panels.py, render.py.

추가한 개발 파일 10개:

- app.py: 메인 스레드의 입력·큐 전달·시작과 종료.
- configuration.py: 기존 config.json 로드와 검증.
- http_client.py: 기존 세션에서 제한된 JSON HTTP 요청.
- analytics_data.py: 집계 API 응답 검증과 표시 허용 목록.
- panel_state.py: request_id/player_id로 연결하는 조회 패널 공통 상태.
- actions_panel.py: 고정 행동 snapshot의 카드·방 목록·오류 안내.
- world.py: 기존 마을·캐릭터·이름표 그리기.
- client/main.py: 교안의 실행 명령을 위한 호환 진입점.
- test_actions_client.py: 행동 조회·계정 경계·비동기 처리·화면 회귀 검사.
- tools/check_routing_docs.py: 파일·문서·색인·시그니처 검사.

삭제하거나 경로를 이동한 개발 파일은 없습니다. 기존 파일 내부 책임을 위 파일로 추출했습니다. 원래 state.py와 history_data.py 및 테스트 3개는 그대로입니다. CC0 PNG·원본 ZIP·라이선스·폰트·출처 설명은 작업 전후 SHA-256이 같습니다.

개발 파일 35개마다 `../files/<상대경로>.md`가 하나씩 있습니다. 문서·검증 결과·작업 전 사본은 개발 파일 대응 대상에서 제외합니다. 문서의 문서를 재귀적으로 만들지 않습니다.

## Git과 변경 전후 구분

[작업 전 상태](git-before.txt)와 [작업 후 상태](git-after.txt)의 `git status --short`는 모두 `not a git repository`입니다. 이 클라이언트에는 Git index가 없으므로 staged·untracked 목록을 확인할 수 없습니다. Git 저장소를 임의로 초기화하거나 add/commit하지 않았습니다.

대신 수정 전 파일 사본과 SHA-256 목록을 보존했습니다.

- [작업 전 파일 목록과 해시](before/baseline-sha256.json)
- [추가·수정·삭제·책임 추출 목록 및 작업 후 해시](change-manifest.json)
- [Git no-index로 생성한 개발 파일 diff](client-changes.diff)

추가 파일의 diff는 빈 파일과 비교했습니다. 기존 사용자 변경을 HEAD 기준으로 되돌리지 않았으며, 이번 작업 시작 시점의 실제 파일과 비교합니다. 새 문서 목록은 change-manifest.json의 documentation_files에 있습니다. 라우팅 색인과 이 검증 기록도 이번에 추가했습니다.

## 검증 결과와 한계

[검사 출력](checks.txt): 회귀 테스트 24개, 개발 파일 35개/짝 문서 35개, 함수 시그니처·색인 일치, 두 진입점의 --check 통과.

테스트는 302/401 및 HTML 본문 미파싱, timeout/오류/미생성과 실제 0의 구분, 중복 버튼 방지, 늦은 응답·다른 계정 응답 제외, 인증 필드 제거, 느린 조회 중 명령 큐 처리, 조회 작업 취소, 기존 snapshot/command_id/version/수련·이력 동작을 확인합니다. 1100×880, 800×640, 550×440에서 렌더링과 조회 버튼 좌표를 검사했습니다.

실제 앱의 headless 시작·QUIT 경로에서 worker 생성 1회, 종료 후 thread 종료와 session=None을 확인했습니다. 이 검증에서는 로그인이나 HTTP를 보내지 않았습니다.

기존 Django URL resolver와 RequestFactory를 사용한 **프로세스 내 view 호출**로 현재 저장된 집계를 읽었습니다. 테스트용 authenticated user 객체를 사용했으며 사용자 비밀번호·세션을 읽거나 생성하지 않았습니다. 실제 브라우저/Pygame 로그인 세션으로 서버에 접속하는 종단 간 검증은 하지 않았습니다. HTTP 계약은 fake aiohttp 응답으로 별도 검증했습니다.

- [허용 목록을 통과한 기존 view 응답](actions-response.json)
- [행동 통계 화면](actions-panel.png)
- [미생성 화면](actions-unavailable.png)
- [7교시 집계 값 기록](day14-transform.md)

화면 캡처의 집계는 실제 저장된 응답입니다. 배경의 플레이어·접속 인원은 화면 확인용 fixture이며 실제 로그인 현황의 증거가 아닙니다. 미생성 화면은 테스트 응답입니다.

검증을 위해 Kafka·Spark·Django 서비스를 새로 띄우지 않았고, 이미 실행 중인 사용자 서비스를 종료하지 않았습니다. 생성한 테스트용 Pygame/worker는 종료했습니다.

## 직접 확인 순서

1. 기존 게임 창을 닫습니다. 코드 변경은 이미 열린 Pygame 창에 자동 반영되지 않습니다.
2. Game-client 폴더에서 `.\.venv\Scripts\python.exe client/main.py` 또는 기존 `.\.venv\Scripts\python.exe main.py`를 실행합니다.
3. 본인이 설정한 계정으로 로그인하고 첫 서버 state와 방 인원을 확인합니다.
4. **대기 · 통계 → 행동 통계**를 누릅니다. source_topic=game.actions.v1, source_kind=bounded-kafka-snapshot, 고유 행동 수, 원본 전달 행 수, 세 카드와 방 목록을 확인합니다.
5. **API 응답 보기 → 행동 통계 응답**에서 경로·status·JSON을 확인합니다. 원본 generated_at은 API 보기에서 UTC 문자열 그대로이며 카드에는 PC 현지 시각을 표시합니다.
6. **다시 조회**를 눌러야 GET이 발생합니다. 이는 저장된 결과의 조회이며 Spark 집계를 새로 실행하지 않습니다. 게임 이동으로 현재 snapshot의 수치가 자동 증가하지 않습니다.
7. 닫기 후 방향키/Space/X수련과 **내 이력 읽기**를 확인합니다. 수련 성공이 이력 패널을 자동으로 열지 않습니다. 서로 다른 계정에서 같은 방의 snapshot·이동 표시도 확인합니다.
8. 로그아웃 후 이전 계정의 조회 내용이 남지 않는지 확인하고 창을 닫습니다.
