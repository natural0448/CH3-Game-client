# 클라이언트 최종 계층화 계획 인수인계

작성일: 2026-09-18

## 요청과 결과

기존 계층화 계획의 초안·보완 이력과 중복 설명을 제거하고, 렌더링·world 분리안과 네트워크 분리안을 하나의 최종 설계로 통합했다.

## 변경 파일

- `docs/client-routing/layering-plan.md`
  - 현재 적용할 최종 구조만 남겼다.
  - network를 port, worker, HTTP, 인증 session, WebSocket play, GET query로 나눴다.
  - 로그인, 재연결, 조회, 로그아웃, 창 종료의 상태와 순서를 명시했다.
  - application/model 상태 소유권과 renderer/world 경계를 통합했다.
- `docs/client-routing/README.md`
  - 계획서 링크 이름과 상태 표현을 최종 설계에 맞췄다.
- `docs/handoffs/2026-09-18-final-layering-plan.md`
  - 이번 문서 작업의 범위와 확인 결과를 기록했다.

## 보존 사항

- Python, 설정, 테스트와 서버 파일은 수정하지 않았다.
- `docs/client-routing/files/`의 1:1 문서는 현재 구현을 설명하므로 변경하지 않았다.
- 계획의 제안 경로는 코드 적용 전이며 현재 구현으로 취급하지 않는다.

## Git 확인

`Game-client`에는 Git 메타데이터가 있지만 현재 branch에 커밋이 하나도 없다. 모든 프로젝트 파일이 untracked 상태이고 staged·tracked diff와 비교 기준 커밋은 없다. 소유권 안전 검사 때문에 일반 `git` 명령은 거부되므로 전역 설정을 바꾸지 않고 확인 명령에만 `safe.directory`를 지정했다. 기존 untracked 파일은 수정 범위로 간주하지 않았으며, 이번 작업에서 직접 바꾼 파일은 위에 적은 문서 세 개다.

## 확인 방법

1. `docs/client-routing/README.md`에서 최종 계획 링크가 열리는지 확인한다.
2. `layering-plan.md`에 과거 초안·보완 이력이 없고 최종 구조만 있는지 확인한다.
3. 코드 구현을 시작할 때 계획의 적용 순서대로 한 단계씩 진행한다.
4. 각 단계가 끝날 때 실제 변경 파일의 1:1 라우팅 문서와 색인을 갱신한다.

## 검증

문서 변경만 수행했으므로 애플리케이션 테스트와 서버 실행은 하지 않았다. Markdown 상대 링크, 코드 fence, 제목 구조는 정적으로 확인했고 모두 정상이다. `python tools/check_routing_docs.py`는 기존 `files/README.md.md`가 대응하는 개발 파일 없이 남아 있어 `orphan: README.md.md`로 실패했다. 이번 계획서 변경에서 발생한 오류가 아니며 요청 범위 밖의 1:1 문서는 삭제하지 않았다.
