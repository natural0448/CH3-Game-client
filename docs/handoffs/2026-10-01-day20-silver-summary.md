# 20일차 Silver summary 표시 호환

## 요청·결과

8교시까지 필요한 수정만 요청받아 기존 전체 통계 패널에서 source=silver와 dataset_version을 읽고 표시하도록 최소 변경했다. Pygame 메인 스레드 그리기와 기존 worker/asyncio/aiohttp 세션·queue·GET 버튼 구조는 유지했다. 서버 URL·로그인·게임 state·광고·로컬 에셋과 폴더 구조는 변경하지 않았다.

## 시작 전 Git과 변경 구분

- Game-client HEAD `6367374 day20 - mission 3`, staged·unstaged·untracked 없음.
- Game-server 기존 사용자 변경과 pipeline 수정은 [서버 인수인계](../../../Game-server/docs/handoffs/2026-10-01-day20-through-period08.md)에 구분했다.
- 이번에 수정: client/contracts/queries.py, client/ui/panels.py, tests/test_actions_ui.py.
- 짝 문서 세 개를 최종 구현에 맞췄다. 추가·이동·삭제된 개발 파일은 없어 기존 1:1 색인을 유지했다. 이 기록과 AST 보고서를 추가했다. 커밋·staging 없음.

## 책임과 계약

- read_analytics는 raw/delta/silver를 허용하며 dataset_version이 있을 때만 문자열 검사 후 복사한다. 기존 다섯 집계 필드와 선택 record_count는 유지하고 알 수 없는 필드는 제외한다.
- draw_analytics는 Silver 원천 문구와 기존 GET 안내 옆 버전을 표시한다. 없는 버전·record_count를 만들지 않는다. 인증 정보·원본 이벤트를 표시하지 않는다.
- 네트워크 조회 모듈은 수정하지 않았다. HTTP redirect/status/Content-Type/timeout 및 로그인 안내 정책은 기존대로다. 게임 좌표·coins·version을 통계로 변경하지 않는다.

## 검사

- `.\.venv\Scripts\python.exe -m unittest discover -s tests -q`: 37개 통과. 기존 UI 테스트에 Silver 원천·버전·쿠키 제외·기존 수치·record_count 미표시 회귀 조건 추가.
- `.\.venv\Scripts\python.exe tools/check_routing_docs.py`: 개발 파일 71개/짝 문서 71개, 시그니처·색인 통과.
- `.\.venv\Scripts\python.exe client/main.py --check`: Python 3.12, pygame-ce 2.5.8, aiohttp 3.14.3, 설정 정상. 서버 연결 안 함.
- 실제 로컬 한글 폰트 13px로 capture-002 포함 caption 너비 317px, 가용 568px 안에 들어감.
- 별도 Spark fixture 결과 → 기존 Django API → read_analytics: HTTP 200, source=silver, dataset_version=capture-001, event_count=4 일치.
- AST routing-doc-auditor: 이번 수정 Python 세 파일의 문서·색인·시그니처 통과. 보고서 docs/client-routing/verification/day20/routing-audit.json.
- Git diff --check 통과. 변경 검증 후 별도로 문서 정합화를 마쳤다.

## 다음 확인

서버 인수인계의 pipeline으로 실제 선택 run을 게시한 뒤 접속기를 재시작한다. 로그인 → 전체 통계 → 새로 읽기 한 번으로 source·dataset_version·generated_at·건수를 API 응답과 비교한다. 실제 운영 자료는 이번 작업에서 교체하지 않았으므로 현재 화면의 기존 Delta 집계가 자동으로 Silver 집계가 되지는 않는다. Spark/Kafka 실행이나 파일 복사를 게임 버튼에 연결하지 않았다.
