# 17일차 클라이언트 라우팅·기획 정합화 인수인계

## 요청 목적과 완료 결과

17일차 `/api/analytics/` raw·delta snapshot 카드의 계층별 호출과 화면 계약을 현재 구현 기준으로 기획에 반영했다. 기존 최종 계층화 계획의 누락·오래된 파일명을 바로잡았다. 이 작업에서는 클라이언트 코드를 추가로 수정하지 않았다.

## 작업 시작 전 Git 상태

- 저장소: `C:\MLO01-01\Chapter3\Game-client`
- 직전 커밋: `c70d4a2 day16-complete`
- staged 변경: 없음
- 작업 시작 전에 존재한 modified: analytics 계약·UI·입력·layout 코드, 대응 라우팅 문서와 두 테스트 파일
- 작업 시작 전에 존재한 untracked: `docs/handoffs/2026-09-28-day17-analytics-card.md`

기존 변경은 사용자 작업으로 취급해 보존했다. README는 기존 변경과 겹치며 이번 작업에서는 17일차 기획 링크를 추가했다.

## 이번 작업의 문서 변경

- 추가: `docs/client-routing/day17-analytics-plan.md`
- 수정: `docs/client-routing/README.md`
- 수정: `docs/client-routing/layering-plan.md`
- 추가: `docs/handoffs/2026-09-28-day17-routing-plan.md`

## 정리한 설계

- 클릭 → intent → Controller → QueryStore/NetworkPort → 기존 worker/AuthSession → allowlist parser → result queue → Pygame panel 호출 흐름
- source raw/delta, 선택적 record_count, 고유 event_count, generated_at과 빈 배열 표시 계약
- HTTP 인증·redirect·Content-Type·timeout과 main-thread Pygame 책임
- 게임 state·광고 slot·시간 창 설명 보존
- Spark 실행 API, Kafka 직접 연결과 모델 학습의 범위 제외

## 계층화 계획 교정

- 실제로 없는 `actions_panel.py` 항목을 제거했다.
- QueryStore, worker dispatch, QueryGateway와 수동 검사 목록에 `windows`를 반영했다.
- lobby와 panels 책임을 현재 파일 구조에 맞췄다.
- analytics의 raw/delta 및 지표 의미를 보존 조건과 검증 기준에 추가했다.

## 검사 결과

- `python tools/check_routing_docs.py`: 69개 개발 파일과 69개 짝 문서 통과
- 전체 단위 테스트: 20개 통과
- 현재 계획 파일 대상 오래된 `actions_panel`·windows 누락 검색: 없음
- `git diff --check`: 통과

과거 검증 자료인 `docs/client-routing/verification/`에는 당시 `actions_panel.py` 기록이 남아 있다. 이는 과거 증거이므로 현재 기획처럼 수정하거나 삭제하지 않았다.

## 다음 확인

실제 서버 로그인 뒤 전체 통계 카드와 API 응답 보기에서 `/api/analytics/`의 source, 생성 시각, record_count, event_count와 행동·방 배열을 대조한다.
