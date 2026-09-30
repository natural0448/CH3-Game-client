# 원본 보존 패널 인수인계

## 요청과 결과

기존 Pygame 접속기의 대기·통계 영역에 **원본 보존** 진입 버튼과 상세 패널을 추가했다. 사용자의 버튼 클릭만 기존 단일 worker에 GET `/api/analytics/lake/`를 전달한다. 같은 ClientSession·인증 쿠키·HTTP 정책을 사용하고, 작은 허용 필드 사전만 결과 queue로 전달한다. Pygame은 메인 스레드에서만 그린다.

ready일 때 dataset_version·rows·bytes·captured_at·generated_at, matched와 local-and-copied-bytes 검사 범위를 표시한다. pending과 unavailable/네트워크 오류는 준비 중과 조회 불가로 구분하고 측정값 0을 만들지 않는다. API 응답 보기에도 원본 보존 항목을 연결했다.

서버의 기존 Lake URL이 상위 prefix와 중복되어 있었으므로 `server/analytics/urls.py`의 경로 문자열 한 곳을 `lake/`로 수정했다. 외부 GET 계약이 요청대로 `/api/analytics/lake/`가 된다. lake_views.py는 사용자가 작성한 파일이며 소스는 수정하지 않았다.

## 작업 시작 전 Git 상태

- Chapter3: Git 상태 확인 불가: 저장소 아님. 저장소를 초기화하지 않았다.
- Game-client: Git 저장소, HEAD `eef4f28 day18-finish`. staged/unstaged/untracked 모두 없음.
- Game-server: Git 저장소, HEAD `b1444ca day19-mission6 complete`. staged 없음.
- Game-server의 작업 시작 전에 존재한 삭제: day18-canonical, day18-load-paths, delta-batch-summary, second-spark-worker 인수인계 네 파일(모두 docs/handoffs/2026-09-28- 접두사). 복원하거나 정리하지 않았다.
- 기존 수정: docs/server-routing/README.md, server/analytics/urls.py, tools/basics/day19_period01.py, tools/check_bronze.py, tools/lake_inventory.py.
- 기존 untracked: docs/handoffs/evidence/day19-period07/의 네 증거 파일, 기존 Bronze 관련 다섯 짝 문서, reports/summary.json, server/analytics/lake_views.py, spark_jobs/bronze_preview.py, tools/basics/day19_period07.py, tools/basics/day19_period08.py, tools/write_lake_contract.py.
- 위 서버 변경은 사용자 작업으로 취급했다. 관련 urls.py와 lake_views.py의 실제 상태를 먼저 문서화하고 경로 수정에 착수했다. 사용자의 기존 import·뷰 구현·다른 경로를 보존했다.

## 이번 개발 파일

| 파일 | 책임과 변경 |
| --- | --- |
| client/contracts/queries.py | read_lake와 고정 GET 명세; status·타입·시각·검사 범위 검증 및 공개 필드 허용 목록 |
| client/network/queries.py | 기존 gateway에 Lake 준비/조회 불가/로그인 안내 연결 |
| client/network/session.py | CookieJar unsafe=True를 루프백 IP에만 허용; DNS 이름과 원격 IP는 기본 정책 |
| client/ui/layout.py | 기존 delivery 버튼 폭을 나누어 lake 진입 추가; 상세 refresh/close Rect와 hit 우선순위 |
| client/ui/input.py | lake 진입·새로고침을 query intent로 변환 |
| client/ui/panels.py | draw_lake와 기존 상세 패널 합성 연결 |
| client/ui/sections/lobby.py | 기존 대기·통계 영역에서 원본 보존 버튼 그리기 |
| client/ui/sections/activity.py | API 응답 보기의 원본 보존 라벨 연결 |
| tests/test_lake_feature.py | 신규 계약·GET·쿠키·오류·그리기·좌표·게임 상태 불변 검사 12개 |
| Game-server/server/analytics/urls.py | 사용자가 추가한 Lake 항목의 중복 prefix 한 줄 수정 |

새 엔진이나 별도 통신 계층을 추가하지 않았다. 기존 폴더를 이동하지 않았다. 현재 프로젝트는 Game-client 루트 config.json과 assets 폴더를 사용하는 구조이므로 이를 유지했다. 실행도 Game-client에서 `python client/main.py`다.

## 경계와 상태 의미

- network는 Pygame을 호출하지 않는다. UI는 HTTP·sleep·Spark·복사를 호출하지 않는다.
- 인증 순서와 WS Origin, 게임 명령/command_id/version, 게임 모델은 수정하지 않았다.
- local-and-copied-bytes는 **선택한 원본과 로컬 사본의 마지막 bytes 비교**이며 현재 시점의 자동 검사나 원격 S3 보장으로 표현하지 않는다.
- CookieJar는 127.0.0.1/::1 등 루프백 IP에서 unsafe=True다. localhost 같은 DNS 이름에서는 기본 정책으로 동작한다. 주소를 자동 치환하거나 127.0.0.1과 localhost를 섞지 않는다.
- 서버 status=ready/pending/unavailable를 유지한다. available은 기존 query 계층을 재사용하기 위해 client parser가 만드는 내부 bool이다.
- 원본 events·player_id 목록·인증 필드·서버의 임의 message는 Lake JSON 허용 목록에 없다.
- 기존 village-board/lobby-banner와 village-ad-slot/lobby-ad-slot Rect는 유지했다.
- 서버 lake-status.json이 없으면 pending이 정상이다. 이 패널의 버튼은 검사 파일을 생성하거나 Spark를 실행하지 않는다.

## 최종 문서 정합화

개발·동작 검증 후 이번에 변경한 아홉 Python 파일의 `docs/client-routing/files/<상대경로>.md`와 색인을 맞췄다. 신규 test_lake_feature.py 문서도 1:1로 추가했다. 시그니처는 routing-doc-auditor의 AST 결과를 기준으로 확인했다.

서버에서는 urls.py 짝 문서를 최종 `lake/` 경로와 맞추고, 기존 사용자 lake_views.py의 짝 문서와 색인을 추가했다. 다른 사용자 소스의 문서는 일괄 재생성하지 않았다.

## 검증 결과

Game-client에서:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p 'test_*.py' -v
.\.venv\Scripts\python.exe client/main.py --check
.\.venv\Scripts\python.exe tools/check_routing_docs.py
.\.venv\Scripts\python.exe C:\Users\이해나\.codex\skills\routing-doc-auditor\scripts\audit_routing.py --repo C:\MLO01-01\Chapter3\Game-client --routing-dir docs/client-routing --format json
git diff --check
```

- 전체 37개 테스트 통과(신규 12개 포함).
- Python 3.12, pygame-ce 2.5.8, aiohttp 3.14.3 진입 검사 통과; 서버 연결을 열지 않는 검사다.
- 프로젝트 문서 검사: 71개 파일/71개 짝 문서, 시그니처·색인 일치.
- 변경 파일 AST 검사: Python 9개/심볼 69개, 문제 0, summary.ok=true.
- 양쪽 저장소 git diff --check 통과. Git의 LF→CRLF 안내는 실패가 아니다.
- 기존 로컬 타일·한글 폰트로 ready/pending/unavailable 화면을 메인 스레드에서 렌더하고 시각 확인했다. 화면은 fixture 입력을 사용한 UI 검증이며 실제 서버 응답 캡처가 아니다.
- 서버에서 resolve/reverse로 정확한 외부 URL 확인. 임시 파일과 RequestFactory를 사용해 미로그인 302, 파일 미생성 pending 200, 정상 ready 200, 손상 JSON unavailable 503을 확인했다. 실제 데이터 파일을 쓰지 않았다.
- 첫 화면 검증에서 API 보기의 lake 라벨 누락을 발견해 수정하고 회귀 검사를 추가했다. 서버 테스트의 첫 RequestFactory 기본 testserver Host는 기존 ALLOWED_HOSTS에 없어 실패했고, 설정을 바꾸지 않고 실제 로컬 Host로 재검증했다.

[AST 보고서](../client-routing/verification/day19-lake/routing-audit.json), [ready 화면](../client-routing/verification/day19-lake/ready.png), [pending 화면](../client-routing/verification/day19-lake/pending.png), [unavailable 화면](../client-routing/verification/day19-lake/unavailable.png).

## 남은 확인과 사용자 실행

현재 켜져 있는 서버에 대한 쿠키 없는 실제 GET은 아직 **404**였다. 저장된 최신 URL 코드에서는 경로 검사가 통과했지만 실행 중인 프로세스 반영은 확인되지 않았다. 해당 서버와 접속기를 재시작한 다음 실제 로그인 조회를 확인해야 한다. 사용자가 운영 중인 서비스를 종료하거나 추가로 띄우지 않았다.

서버 터미널에서 기존 프로세스를 Ctrl+C로 종료한 후:

```powershell
cd C:\MLO01-01\Chapter3\Game-server
.\server\.venv\Scripts\python.exe server/manage.py runserver --noreload 127.0.0.1:8000
```

접속기 터미널에서 기존 창을 종료하고:

```powershell
cd C:\MLO01-01\Chapter3\Game-client
.\.venv\Scripts\python.exe client/main.py
```

로그인 → 대기·통계의 원본 보존 → 상세 새로고침 → API 응답 보기와 공개 필드 대조 → 로그아웃 → 창 종료 순서로 확인한다.

서버 전체 변경 AST 검사 당시에는 이번 요청 밖의 기존 사용자 파일 tools/basics/day19_period08.py와 tools/write_lake_contract.py의 문서·색인 누락 네 건이 있었다. 이번 서버 변경 대상 urls.py 및 관련 lake_views.py는 문서/색인/시그니처가 일치한다. 실제 계정으로 로그인한 HTTP/WS 종료 검증은 이번에 수행하지 않았고 위 사용자 순서로 확인한다. 에이전트는 두 저장소에서 stage/commit을 수행하지 않았다.

마감 확인 중 서버 HEAD가 외부 작업으로 `0d22f22 day19-finish`로 바뀌었다. 위 서버 경로·문서 변경도 그 커밋에 포함되어 현재 소스 working diff에는 표시되지 않는다. 이후 생긴 untracked tools/basics/day20_period01.py는 이번 요청 밖의 사용자 작업으로 보존했다. 클라이언트 HEAD는 eef4f28이고 이번 접속기 변경은 working tree에 남아 있다.
