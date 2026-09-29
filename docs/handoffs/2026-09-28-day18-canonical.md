# 2026-09-28 Pygame 접속기 현재 구현 정본

상태: **구현 반영 / 검증 완료**  
기준 저장소: `C:/MLO01-01/Chapter3/Game-client`  
기준 커밋: `c70d4a2 day16-complete` + 아래 작업 트리 변경

이 문서는 2026-09-28 종료 시점의 읽기 전용 분석 조회와 Pygame 표시 구조를 한 곳에서 찾기 위한 정본이다. 실제 함수·메서드 계약은 `docs/client-routing/README.md`와 각 1:1 짝 문서를 기준으로 한다. `day17-analytics-plan.md`는 구현 완료 상태의 기능 설명이고 이전 인수인계는 작업 과정 기록으로 유지한다.

## 1. 현재 호출 구조

```text
Pygame 클릭
  → ui.input이 query intent 생성
  → application Controller·QueryStore가 request_id와 busy 상태 관리
  → NetworkPort가 기존 단일 worker queue에 요청 전달
  → worker의 같은 asyncio loop·AuthSession·aiohttp ClientSession으로 GET
  → contracts.queries가 허용 필드만 단순 dict로 변환
  → thread-safe 결과 queue
  → 메인 스레드가 QueryStore 갱신 후 Pygame 카드 렌더링
```

worker는 Pygame 객체를 만들지 않고 UI는 aiohttp를 알지 않는다. 조회 결과는 좌표, coins, version과 미완료 게임 명령을 변경하지 않는다. 302/401과 HTML은 로그인 안내로 처리하고 인증 정보는 queue·화면·로그에 남기지 않는다.

## 2. 오늘 반영된 조회 카드

- `/api/analytics/`: raw·Delta 확정 사실 snapshot, 생성 시각, 고유 사실 수, 선택적 원천 행 수, 행동·방 표.
- `/api/analytics/actions/`: action label이 적용된 고정 행동 snapshot.
- `/api/analytics/ingest/`: Kafka 수집 레코드·고유 사건·재전달 레코드.
- `/api/analytics/windows/`: tumbling·sliding 시간 창 결과.
- `/api/analytics/load/`: 저장된 최근 수업 부하 측정, 방별 실행 범위와 최다 성공 응답 방. 동률은 `room_id` 오름차순으로 결정한다.
- `/api/analytics/metrics/`: DB 최근 확정 사실, publisher 표시, Kafka lag와 별도 Spark progress 시각.

모든 조회는 사용자가 해당 버튼을 누를 때 GET 한 번만 수행한다. 버튼은 Spark 작업, Kafka 연결, 동시 접속 측정이나 모델 학습을 시작하지 않는다. `available=false`, 오류, 빈 배열과 실제 0건은 각각 다른 문구로 표시한다.

## 3. 오늘 작업 트리의 개발 파일

### 수정

- `client/contracts/queries.py`: analytics/load/metrics 포함 읽기 응답 allowlist와 타입 검증.
- `client/network/worker.py`: `QUERY_SPECS` 기준 query dispatch.
- `client/ui/input.py`, `client/ui/layout.py`: 조회 진입·새로 읽기·닫기 intent와 동일 좌표 hit test.
- `client/ui/panels.py`: 전체·행동·수집·시간 창·부하·운영 지표 카드와 최다 응답 방 표시.
- `client/ui/sections/lobby.py`, `client/ui/sections/activity.py`: 조회 버튼과 API 응답 source 라벨.
- `tests/test_actions_ui.py`, `tests/test_network_queries.py`: 기존 통계 카드·HTTP 경계 회귀 검사 확장.

### 추가

- `tests/test_day18_metrics.py`: load/metrics GET, allowlist, 미생성·401, 단위·시각·입력 회귀 검사.
- `docs/client-routing/day17-analytics-plan.md`: 구현된 raw·delta 분석 카드의 책임 흐름과 화면 계약.

각 개발 파일의 짝 문서와 `docs/client-routing/README.md` 색인을 현재 코드에 맞췄다.

## 4. Git 기준과 변경 소유권

- 작업 시작·종료 기준 커밋: `c70d4a2 day16-complete`.
- staged 변경: 없음.
- 작업 트리에는 17일차 분석 카드 변경과 18일차 부하·운영 카드 변경이 함께 있다.
- 작업 시작 시 이미 존재한 변경은 사용자 작업으로 취급하고 기존 계층, 광고 slot, 로컬 asset, WebSocket과 게임 state 계약을 보존했다.
- 비밀번호, Cookie, session, CSRF와 `.env` 값은 diff나 문서에 기록하지 않았다.

## 5. 라우팅 문서 정합화

- 색인: `docs/client-routing/README.md`.
- 자동 검사 기준 개발 파일 70개와 짝 문서 70개가 일치한다.
- 변경한 contracts, worker, input, layout, panels, lobby, activity와 테스트 문서는 실제 시그니처·파라미터·의사코드·직접 호출·값 출처를 반영한다.
- `layering-plan.md`는 현재 반영된 책임 경계와 앞으로 유지할 기준을 구분해 기록한다.
- 과거 `verification/` 문서는 당시 증거이므로 현재 라우팅 정본 대신 사용하지 않는다.

## 6. 검증 결과

```text
python -m unittest discover -s tests -p "test_*.py" -v
결과: 25 tests passed

python tools/check_routing_docs.py
결과: 70 client files, 70 paired documents; signatures and index match

python client/main.py --check
결과: Python 3.12, pygame-ce 2.5.8, aiohttp 3.14.3, Config OK

python -m py_compile [오늘 변경한 Python 파일]
결과: 성공
```

실제 계정으로 로그인한 GUI 수동 확인은 반복하지 않았다. 조회 계약 검사는 fake session과 메인 스레드 Pygame smoke test로 수행했다.

## 7. 다음 확인 순서

서버의 `game-summary.json`, `game-metrics.json`을 필요한 시점에 갱신하고 Django를 실행한 뒤 접속기를 시작한다.

```powershell
cd C:\MLO01-01\Chapter3\Game-client
.\.venv\Scripts\python.exe client\main.py
```

로그인 후 `전체`, `최근 수업 측정`, `분석 전달 상태`를 각각 한 번 눌러 카드와 API 응답 보기의 경로·status·허용 JSON을 대조한다. 조회 전후 캐릭터 좌표·coins·version이 바뀌지 않는지도 확인한다.

서버의 같은 날짜 정본은 `C:/MLO01-01/Chapter3/Game-server/docs/handoffs/2026-09-28-day18-canonical.md`다.
