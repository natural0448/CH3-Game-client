# 16일차 4교시 watermark 도움말 인수인계

## 요청 목적과 결과

Spark 시간 창의 완료 시점과 게임 명령 완료 시점을 혼동하지 않도록 행동 통계 패널에 교안의 watermark 도움말을 추가했다. 기존 조회 요청, 서버 state, 네트워크 worker와 API 계약은 바꾸지 않았다.

## 작업 시작 전 Git 상태

- 저장소: `C:/MLO01-01/Chapter3/Game-client`
- 직전 커밋: `ef2cc02 commit - day15`
- staged·unstaged·untracked 파일: 없음

## 변경 파일

- 수정: `client/ui/panels.py`
- 수정: `tests/test_actions_ui.py`
- 수정: `docs/client-routing/files/client/ui/panels.py.md`
- 수정: `docs/client-routing/files/tests/test_actions_ui.py.md`
- 추가: 이 인수인계 문서

## 동작과 책임 경계

- `draw_actions`가 기존 서버 응답을 읽어 메인 스레드에서 도움말만 그린다.
- 도움말은 확정 사실 수집, 뒤 시각 입력에 따른 watermark 진행, 창 확정, 요약 갱신과 조회 순서를 설명한다.
- 기존 접속자 수·잔액·현재 이동 횟수 안내를 유지한다.
- 두 안내를 겹치지 않게 표시하기 위해 방별 목록을 페이지당 4행에서 3행으로 바꿨다.
- 버튼은 기존 GET만 수행하며 Spark 작업을 시작하지 않는다.

## 라우팅 문서

- `client/ui/panels.py`와 짝 문서의 방별 페이지 크기·도움말 동작을 맞췄다.
- `tests/test_actions_ui.py`와 짝 문서에 도움말 검증을 반영했다.
- 파일 추가·이동·삭제가 없어 라우팅 색인 항목은 변경하지 않았다.

## 검사 결과

```powershell
.\.venv\Scripts\python.exe tools\check_routing_docs.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -p 'test_*.py' -v
.\.venv\Scripts\python.exe client\main.py --check
```

- 라우팅 검사: 68개 개발 파일과 68개 짝 문서, 시그니처·색인 일치
- 테스트: 14개 모두 통과
- 실행 설정 검사: Python 3.12, pygame-ce 2.5.8, aiohttp 3.14.3 확인; 서버 연결 없음

## 다음 확인 순서

게임 서버와 접속기를 실행해 로그인한 뒤 행동 통계 패널을 연다. 기존 통계 값과 안내 문구가 함께 보이고, 방별 목록이 3행 단위로 이동하는지 확인한다. 이 화면 확인은 Spark query나 Kafka를 자동으로 시작하지 않는다.
