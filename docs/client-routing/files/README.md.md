# README.md

## 책임과 값 출처

사용자가 실행·검사 명령과 최종 계층의 위치를 찾는 안내서다. 값은 실제 `client/`, `tests/`, `config.json`, `assets/` 경로에서 온다. 외부 코드를 호출하지 않는다.

## 내용

```text
실행: .venv\Scripts\python.exe client\main.py
오프라인 확인: client\main.py --check
테스트: unittest discover -s tests
문서 검사: tools\check_routing_docs.py
행동 통계: 버튼 요청의 GET /api/analytics/actions/
```
