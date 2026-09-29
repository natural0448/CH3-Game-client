# 17일차 8교시 전체 통계 카드 인수인계

## 요청 목적과 완료 결과

Pygame 접속기의 기존 `/api/analytics/` 통계 카드를 17일차 8교시 응답 계약에 맞췄다.

- 기존 worker asyncio loop, `aiohttp.ClientSession`, 독립 인증 세션과 thread-safe queue를 그대로 사용한다.
- `source=raw`는 `DB 내보내기 스냅샷`, `source=delta`는 `event_id별 고유 사실 Delta`로 표시한다.
- `event_count`는 `고유 확정 사실 수`, 선택적 `record_count`는 `선택한 원천의 행 수`로 구분한다.
- `generated_at`만 `집계 생성 시각`으로 표시한다.
- 행동·방 배열이 비었을 때 게시할 그룹이 없다는 상태를 표시한다.
- 카드 안에 `새로 읽기` 버튼을 추가하고 기존 query intent로 GET 한 번만 요청한다.
- available=false, 오류와 미조회 상태를 실제 0건으로 만들지 않는다.

## 작업 시작 전 Git 상태

- 저장소: `C:\MLO01-01\Chapter3\Game-client`
- 직전 커밋: `c70d4a2 day16-complete`
- staged 변경: 없음
- unstaged 변경: 없음
- untracked 파일: 없음

## 이번 작업의 파일 변경

개발 파일 수정:

- `client/contracts/queries.py`
- `client/ui/panels.py`
- `client/ui/layout.py`
- `client/ui/input.py`
- `tests/test_network_queries.py`
- `tests/test_actions_ui.py`

라우팅 문서 수정:

- `docs/client-routing/README.md`
- `docs/client-routing/files/client/contracts/queries.py.md`
- `docs/client-routing/files/client/ui/panels.py.md`
- `docs/client-routing/files/client/ui/layout.py.md`
- `docs/client-routing/files/client/ui/input.py.md`
- `docs/client-routing/files/tests/test_network_queries.py.md`
- `docs/client-routing/files/tests/test_actions_ui.py.md`

추가:

- `docs/handoffs/2026-09-28-day17-analytics-card.md`

이동·삭제한 파일은 없다.

## 중요한 설계 결정과 책임 경계

- 계약 계층은 analytics의 허용 필드만 복사한다. source는 raw/delta만 허용하고 record_count는 응답에 있을 때만 보존한다.
- network 계층은 수정하지 않았다. 기존 JSON Content-Type, redirect 차단, timeout, 로그인 오류와 동일 세션 정책이 이미 요구사항을 충족한다.
- application 상태와 서버 확정 GameState는 수정하지 않았다. 통계가 좌표·coins·version을 변경하지 않는다.
- input은 `analytics_refresh`를 기존 analytics query intent로 번역할 뿐이며 HTTP를 호출하지 않는다.
- Pygame 카드와 표는 메인 스레드 renderer에서만 그린다.
- `draw_windows`, `village-board`, `lobby-banner`와 로컬 asset 로딩은 수정하지 않았다.

## 라우팅 문서 정합화

변경한 여섯 개발 파일의 짝 문서에 실제 parser 필드, 표시 문구, control, intent와 테스트 메서드를 반영했다. 색인의 패널·테스트 책임 설명도 현재 구현과 일치시켰다.

## 실행한 검사

- `python -m py_compile client/contracts/queries.py client/ui/panels.py client/ui/layout.py client/ui/input.py`: 통과
- `python -m unittest tests.test_network_queries -v`: 5개 통과
- `python -m unittest tests.test_actions_ui -v`: 5개 통과
- `python tools/check_routing_docs.py`: 69개 개발 파일과 69개 짝 문서, 시그니처·색인 검사 통과
- `python -m unittest discover -s tests -p "test_*.py" -v`: 20개 통과
- `python client/main.py --check`: Python 3.12, pygame-ce, aiohttp와 설정 확인 통과; 서버 연결 없음
- `git diff --check`: 통과

## 실행하지 못한 검사와 남은 위험

- 실제 로그인 세션을 사용하는 서버 연동 화면은 실행하지 않았다.
- 서버가 available=true를 반환할 때 source는 raw 또는 delta여야 한다. 그 외 값은 계약 오류로 표시한다.
- generated_at은 timezone을 포함해야 한다.

## 다음 확인 순서

```powershell
cd C:\MLO01-01\Chapter3\Game-client
.\.venv\Scripts\python.exe client\main.py
```

로그인 후 대기·통계의 `전체` 버튼을 누르고 카드에서 원천, 고유 확정 사실 수, 선택적 원천 행 수, 집계 생성 시각과 행동·방 표를 확인한다. `새로 읽기`를 한 번 누른 뒤 API 응답 보기에서 `GET /api/analytics/`, status와 허용 JSON을 카드 값과 대조한다.
