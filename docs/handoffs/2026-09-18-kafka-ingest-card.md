# Kafka 수집 통계 카드 인수인계

## 요청 목적과 완료 결과

기존 로컬 Pygame 접속기에 버튼형 `GET /api/analytics/ingest/` 조회와 “Kafka 수집 통계” 카드를 추가했다. 기존 단일 `NetworkWorker`, asyncio loop, `ClientSession`, queue 경계와 메인 스레드 Pygame 렌더링을 유지했다. 서버 코드, URL, 게임 state, WebSocket 명령 형식은 변경하지 않았다.

카드는 `source`, `generated_at`, 수집 레코드, 고유 사건, 재전달 레코드와 `by_action`의 event_type/count를 표시한다. 미생성 상태는 숫자를 만들지 않으며 503은 “마지막 수집 통계를 읽을 수 없음”, 401은 로그인 안내로 표시한다. 조회 버튼은 이미 게시된 결과만 읽고 Spark를 실행하지 않는다.

## 작업 시작 전 Git 상태

- 저장소: `C:/MLO01-01/Chapter3/Game-client`.
- 직전 커밋: `0810283 라우팅 문서를 활용한 전체 파일 수정`.
- staged, unstaged, untracked 변경: 모두 없음.

따라서 이번 최종 변경 목록은 모두 이 작업에서 발생했다.

## 변경 파일

코드:

- `client/contracts/queries.py`
- `client/network/queries.py`
- `client/network/worker.py`
- `client/ui/input.py`
- `client/ui/layout.py`
- `client/ui/panels.py`
- `client/ui/sections/activity.py`
- `client/ui/sections/lobby.py`

테스트:

- `tests/support.py`
- `tests/test_network_queries.py`
- `tests/test_actions_ui.py`

라우팅 문서:

- `docs/client-routing/README.md`
- `docs/client-routing/layering-plan.md`
- 위 코드·테스트 파일에 대응하는 `docs/client-routing/files/...` 문서 11개

인수인계:

- `docs/handoffs/2026-09-18-kafka-ingest-card.md`

이동·삭제 파일은 없다.

## 설계 결정과 책임 경계

- `contracts.queries.read_ingest`는 허용된 표시 필드만 복사하며 raw_value, evidence, 인증 정보는 전달하지 않는다.
- `QUERY_SPECS`의 `ingest`가 고정 GET 경로와 미생성 안내를 소유한다.
- `QueryGateway`는 같은 인증 세션으로 GET하고 결과 queue에 안전한 dict만 넣는다. 503 문구 변환도 이 네트워크 조회 경계에서 수행한다.
- `QueryStore`와 Controller의 기존 동적 query 상태·상관관계를 그대로 재사용했다.
- `InputRouter`는 ingest 진입·새로 읽기 클릭을 query intent로만 변환한다.
- `draw_ingest`는 메인 스레드에서 전달된 QueryView만 그리고 요청이나 상태 변경을 수행하지 않는다.
- API 응답 보기 source 순환에 ingest를 추가했다.
- 기존 analytics/actions/delivery/history, 광고 slot, 로컬 에셋과 게임 렌더링은 유지했다.

## 문서 정합화

변경된 개발 파일의 기존 1:1 문서만 갱신했다. 색인의 책임 설명과 현재 계층 문서의 query 집합도 `ingest`를 포함하도록 맞췄다. 새 개발 파일은 없어서 라우팅 색인에 새 경로는 추가하지 않았다.

## 검사 결과

- `python tools/check_routing_docs.py`: 68개 개발 파일과 68개 문서, 시그니처·색인 일치.
- `python -m unittest discover -s tests -p "test_*.py" -v`: 14개 테스트 통과.
- `python client/main.py --check`: Python 3.12, pygame-ce 2.5.8, aiohttp 3.14.3, 설정 검사 통과. 서버 연결 없음.
- 실제 `Game-server/data/marts/stream-summary.json`을 `read_ingest`로 검증: source `kafka-parquet`, record/event/duplicate와 세 행동 목록 정상.
- 1100×880 오프스크린 렌더링: 카드, 세 count 영역, 행동 목록, 통계 버튼 3개가 영역 안에 표시됨. “통계 다시 읽기” 버튼 폭을 글자에 맞게 조정했다.
- `git diff --check`: 공백 오류 없음. 출력된 LF→CRLF 문구는 Windows 작업 트리의 줄바꿈 안내다.

실제 계정의 쿠키가 필요한 UI 로그인→GET 통합 확인은 자동 실행하지 않았다. 비밀번호·쿠키·세션·CSRF는 기록하지 않았다.

## 다음 확인 순서

서버가 실행되고 `stream-summary.json`이 준비된 상태에서 다음을 실행한다.

```powershell
cd C:\MLO01-01\Chapter3\Game-client
.\.venv\Scripts\Activate.ps1
python client\main.py
```

로그인 후 대기·통계 영역의 `수집 통계`를 누른다. 카드에서 source와 세 count, 행동 목록을 확인하고 `통계 다시 읽기`가 클릭할 때만 갱신되는지 확인한다. API 응답 보기에서 `수집 통계 응답`을 선택하면 `GET /api/analytics/ingest/`, status, 허용 JSON만 보여야 한다.

