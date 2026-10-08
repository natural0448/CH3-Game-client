# 2026-10-08 접속기 광고 라우팅 문서 검수

## 요청과 결과

현재까지 진행한 구현을 라우팅 문서에 맞추는 요청 중 Game-client를 서브에이전트가 검수했다. 실제 day23 광고 선택·이미지·노출·클릭 경로를 유지하고 네트워크 계층의 짝 문서와 색인을 보강했다. 개발 소스·설정·데이터는 수정하지 않았다.

## 작업 시작 Git 상태

- Git 저장소: `C:/MLO01-01/Chapter3/Game-client`; 하위 AGENTS.md 없음, Chapter3/AGENTS.md 적용.
- HEAD: `0c8d5a2 day23 진행사항`.
- `git status --short`, `git diff --name-status`, `git diff --cached --name-status`: 모두 빈 출력. 기존 staged·unstaged·untracked 파일 없음.
- AST 보고서는 이번 검수에서 새로 생성한 증거다. 커밋된 day23 소스 구현은 기존 상태이며 이번 작업으로 주장하지 않는다.

## 변경 파일

- 수정: `docs/client-routing/files/client/network/ads.py.md` — 실제 게임 선택 API·같은 origin PNG·사건 위임, 상태 초기값과 PNG 제한을 기록.
- 수정: `docs/client-routing/files/client/network/session.py.md` — 실제 timeout 범위 `0 < timeout <= 30`초로 정정, 게임 사건 API와 공개 receipt 경계를 기록.
- 최종 검토 후 같은 두 짝 문서의 직접 호출 기대 계약을 해당 파일이 실제 호출하는 AuthSession/JsonHttpClient·계약 parser·aiohttp·asyncio·queue callback 범위로 정정했다. 빈 기반클래스/호출 표현은 명시적 기반클래스 없음·직접 호출 없음으로 고쳤다.
- 수정: `docs/client-routing/README.md` — 이번 검수 링크와 day24 접속기 소비·전달 미적용 경계를 추가. 개발 파일 추가·이동·삭제가 없어 기존 1:1 색인 항목은 유지.
- 추가: 이 인수인계와 `docs/client-routing/verification/day24-routing-sync/agent-client-*.json` 검증 증거.
- 코드·설정·테스트 변경, 파일 이동·삭제, stage/commit/push 없음.

## 확인한 책임과 직접 호출

| 구현 파일 | 주요 실제 함수 | 직접 책임 |
|---|---|---|
| `client/application/controller.py` | `Controller.request_ad(self, slot_id, now=None)`, `Controller.request_ad_event(self, slot_id, event_type, now=None)`, `Controller.confirm_ad_display(self, receipts, failures=None, now=None)` | 현재 Player와 표시 상태를 확인하고 기존 NetworkPort queue 요청으로 연결 |
| `client/application/ads.py` | `AdSlot.request(self, player_id, now)`, `AdSlot.request_event(self, event_type, player_id, now)`, `AdSlot.accept_event(self, event, player_id, now)`, `AdStore.mark_displayed(self, receipts, now=None, failures=None)` | 표시·선택·사건 확인과 재시도 상태를 소유; HTTP를 직접 호출하지 않음 |
| `client/network/ads.py` | `AdGateway.fetch(self, request)`, `AdGateway.fetch_png(self, path)`, `AdGateway.fetch_event(self, request)` | AuthSession 선택 POST, 같은 게임 origin PNG GET, AuthSession 사건 위임; 현재 generation 결과만 queue로 전달 |
| `client/network/session.py` | `AuthSession.post_ad_event(self, decision_id: str, event_type: str) -> dict` | 게임 CSRF GET 후 같은 로그인 세션의 `/api/ads/events/` POST; 공개 receipt dict 또는 오류 |
| `client/contracts/ads.py` | `read_decision(data, slot_id)`, `read_ad_event(data, decision_id, event_type)` | 허용 공개 선택·사건 응답과 SLOTS/EVENT_TYPES/CREATIVE_PATHS 계약 |
| `client/ui/ads.py`, `client/ui/renderer.py`, `client/app.py` | `AdsRenderer.draw(self, painter, ads, authenticated)`, `ScreenRenderer.render(self, model, layout, fps)`, `run(config)` | 메인 스레드 decode·draw·flip 후 receipt를 Controller로 전달 |

이 파일들은 기존 `docs/client-routing/files/<소스 경로>.md`와 1:1 대응하며 모두 색인에 존재한다. 직접 선택 API는 `/api/ads/decision/`이고 사건 API는 `/api/ads/events/`다. 광고 서버 media API 인증·저장은 게임 서버 뒤의 책임이다. 접속기 광고 계층에는 `player-cdc.ndjson` 또는 data/exports 파일을 읽는 경로가 없다. 서버 측 day24 내보내기를 접속기 구현으로 기록하지 않는다.

## 검사와 결과

1. routing-doc-auditor 먼저 실행: bundled Python `-X utf8`와 `--repo C:/MLO01-01/Chapter3/Game-client --routing-dir docs/client-routing --include-all --format json --output docs/client-routing/verification/day24-routing-sync/agent-client-before.json`. 전체 70 Python 파일/439 symbol 중 18 issue, 모두 `docs/client-routing/verification/before`의 보존 사본 9개에 대한 짝 문서·색인 항목이다. 현재 개발 파일에는 issue 없음. 보고서를 근거로 광고 관련 경계만 확인했다.
2. 문서 갱신 후 같은 범위 재검사: `agent-client-after.json`은 70 Python/439 symbol, 같은 보존 사본 18 issue다. 전체 결과와 별도로 현재 개발 파일에서 보존 docs를 제외한 `agent-client-maintained.json`에 범위·예외를 명시한다. 유지되는 Python 파일 61개/338 symbol, issue=0, summary.ok=true다. 보존 사본에 재귀 짝 문서를 만들거나 기존 기록을 삭제하지 않았다.
3. `.\.venv\Scripts\python.exe -X utf8 tools/check_routing_docs.py`: 77개 개발 파일/77개 짝 문서, signature·색인 일치 PASS.
4. `.\.venv\Scripts\python.exe -X utf8 -m unittest tests.test_ads_events tests.test_ads_feature -v`: 광고 회귀검사 20개 PASS. 인증/CSRF·공개 receipt·PNG·표시 실패·로비 사건 미전송·재시도·영구 거절·늦은 결과·queue 오류 검증.
5. `git diff --check`: exit 0 PASS. Git의 LF→CRLF 설정 알림 외 오류 없음.

종료 Git 상태: 짝 문서 2개와 색인 1개가 modified이며 이번 인수인계 및 `verification/day24-routing-sync/`가 untracked다. staged 변경과 소스 변경은 없다. 시작이 clean이었으므로 위 목록은 모두 이번 문서 검수 변경으로 구분된다.

최종 직접 호출 설명 정정 뒤 AST 보고서와 기존 routing 검사를 다시 확인했다. 코드·설정·테스트 변경이 없으므로 기존 광고 테스트 20개 PASS를 유지하고 다시 실행하지 않았다.

최초 시스템 `python` 실행에서는 Python3.14 위치 경고 및 cp949 subprocess 디코딩 오류가 발생했다. UTF-8 모드의 bundled Python으로 재검사했으며 위 결과는 재검사 기준이다. 광고 기능 테스트는 기존 Python3.12 가상환경으로 통과했다.

## 한계와 다음 확인

이번 검수는 문서와 현재 코드·기존 로컬 회귀검사 범위다. 실제 학생 창 로그인·노출·클릭 관찰과 두 서버 운영 DB 연결 검사는 실행하지 않았다. 문서만 수정한 작업으로 서버·DB·NDJSON 파일은 건드리지 않았다. 실제 사용 시 Game-client README의 기존 로그인 → 마을 게시판 표시 → 노출 완료 → 실제 광고 카드 클릭 순서를 따른다.

문서 검사 재실행은 Game-client 루트에서 `.\.venv\Scripts\python.exe -X utf8 tools/check_routing_docs.py`다. 사용자에게 별도 적용·이동·재내보내기 명령은 필요하지 않다.
