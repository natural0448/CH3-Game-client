# Game-client

Python 3.12와 pygame-ce, aiohttp로 실행하는 작은 마을 접속기다. 서버 계약과 게임 규칙은 변경하지 않으며, 클라이언트는 서버가 확정한 state와 snapshot만 화면에 반영한다.

## 실행

```powershell
cd C:\MLO01-01\Chapter3\Game-client
.\.venv\Scripts\python.exe client\main.py --check
.\.venv\Scripts\python.exe client\main.py
```

`--check`는 설정과 의존성만 확인하며 서버에 연결하지 않는다.

## 구조

- `client/application`: 사용자 의도, 조회 상관관계, 읽기 전용 화면 모델
- `client/model`: 서버가 확정한 플레이어·방·명령 상태
- `client/contracts`: HTTP와 WebSocket 응답 검증 및 허용 필드
- `client/network`: 단일 worker의 세션, HTTP, WebSocket, 조회 작업
- `client/ui`: 메인 스레드 입력, Layout, Pygame 표시, 마을 장면
- `tests`: 서버를 켜지 않고 실행하는 계약·상태·표시 회귀 검사

행동 통계는 사용자가 버튼을 눌렀을 때만 같은 인증 세션으로 `GET /api/analytics/actions/`를 호출한다. Spark 작업 실행이나 Kafka 연결을 요청하지 않는다.

## 검사

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py" -v
.\.venv\Scripts\python.exe tools\check_routing_docs.py
```

에셋의 라이선스와 출처는 `assets/README.md`와 `assets/sources/`를 따른다.
