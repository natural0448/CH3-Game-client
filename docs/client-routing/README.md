# 클라이언트 라우팅 지도

읽기 순서: 이 색인 → 관련 파일 문서 → 필요한 코드. 전체 저장소 탐색은 하지 않습니다.

[최종 계층화 실행 계획](layering-plan.md)은 라우팅 문서만 근거로 작성한 **코드 적용 전 설계**입니다. 현재 구현 지도는 아래 색인과 파일별 문서를 기준으로 읽습니다.

## 문서 범위와 표기

개발 루트는 `Game-client/`입니다. `files/<개발 루트 상대경로>.md`가 개발 파일 하나와 정확히 대응합니다. 코드·테스트·설정·에셋·라이선스 파일을 포함합니다. `.venv/`, `__pycache__/`, `.git/`, 실행 로그와 문서 트리 `docs/`는 대상에서 제외합니다. 문서의 문서를 재귀 생성하지 않습니다.

각 파일 문서는 그 계층의 책임과 직접 import/호출만 설명합니다. 하위 계층 내부나 서버 구현을 펼치지 않습니다. 함수는 실제 시그니처·파라미터·의사코드·직접 호출을 기록합니다. 변수/상수의 실제 값 또는 값이 오는 표현식은 전역 표와 의사코드의 `설정/갱신/반복`에 기재합니다. 동적인 결과값은 실행 중 값 대신 출처를 적습니다.

## 계층별 직접 연결

```text
client/main.py → main.py → configuration.load_config / app.run
app.run → NetworkWorker.submit/events / VillageState / Renderer.query_panels
NetworkWorker → http_client.request_json / analytics_data / history_data / state 검증
Renderer → world.draw_world / AnalyticsPanel / HistoryPanel / ActionsPanel
조회 패널 → QueryPanel (request_id·player_id·화면 상태만)
worker → 결과 queue → app → 패널 상태 → 메인 스레드 draw
```

통신과 표시의 경계는 request/result dict입니다. GET 통계는 게임 명령과 다른 request_id를 사용하며 Player coins·좌표·version을 변경하지 않습니다. 기존 command_id/epoch/version·독립 세션·CSRF·Origin·snapshot은 유지합니다.

## 수정 위치 빠른 선택

|작업|먼저 읽을 파일 문서|
|---|---|
|실행·버튼·종료|main.py → app.py|
|GET 경로·세션·응답 큐|network.py → http_client.py|
|행동 응답 필드·검증|analytics_data.py|
|행동 카드·미생성 문구·방 목록|actions_panel.py → panel_state.py|
|이력·기존 집계·API 표시|panels.py|
|마을·캐릭터·화면 크기|render.py → world.py|
|게임 상태·명령 대기|state.py|

## 파일별 1:1 색인

|개발 파일|계층·책임|짝 문서|
|---|---|---|
|`.gitignore`|관리 제외|[.gitignore](files/.gitignore.md)|
|`actions_panel.py`|행동 집계 표시|[actions_panel.py](files/actions_panel.py.md)|
|`analytics_data.py`|응답 검증|[analytics_data.py](files/analytics_data.py.md)|
|`app.py`|앱 제어|[app.py](files/app.py.md)|
|`assets/fonts/LICENSE`|정적 에셋|[assets/fonts/LICENSE](files/assets/fonts/LICENSE.md)|
|`assets/fonts/NotoSansCJKkr-Regular.otf`|정적 에셋|[assets/fonts/NotoSansCJKkr-Regular.otf](files/assets/fonts/NotoSansCJKkr-Regular.otf.md)|
|`assets/grass.png`|정적 에셋|[assets/grass.png](files/assets/grass.png.md)|
|`assets/hero.png`|정적 에셋|[assets/hero.png](files/assets/hero.png.md)|
|`assets/house.png`|정적 에셋|[assets/house.png](files/assets/house.png.md)|
|`assets/path.png`|정적 에셋|[assets/path.png](files/assets/path.png.md)|
|`assets/README.md`|정적 에셋|[assets/README.md](files/assets/README.md.md)|
|`assets/sources/dungeon-License.txt`|정적 에셋|[assets/sources/dungeon-License.txt](files/assets/sources/dungeon-License.txt.md)|
|`assets/sources/kenney_tiny-dungeon.zip`|정적 에셋|[assets/sources/kenney_tiny-dungeon.zip](files/assets/sources/kenney_tiny-dungeon.zip.md)|
|`assets/sources/kenney_tiny-town.zip`|정적 에셋|[assets/sources/kenney_tiny-town.zip](files/assets/sources/kenney_tiny-town.zip.md)|
|`assets/sources/town-License.txt`|정적 에셋|[assets/sources/town-License.txt](files/assets/sources/town-License.txt.md)|
|`assets/tree.png`|정적 에셋|[assets/tree.png](files/assets/tree.png.md)|
|`client/main.py`|호환 진입|[client/main.py](files/client/main.py.md)|
|`config.json`|설정 데이터|[config.json](files/config.json.md)|
|`configuration.py`|설정|[configuration.py](files/configuration.py.md)|
|`history_data.py`|응답 검증|[history_data.py](files/history_data.py.md)|
|`http_client.py`|HTTP 전송|[http_client.py](files/http_client.py.md)|
|`main.py`|진입·조립|[main.py](files/main.py.md)|
|`network.py`|네트워크 조정|[network.py](files/network.py.md)|
|`panel_state.py`|조회 패널 상태|[panel_state.py](files/panel_state.py.md)|
|`panels.py`|조회 표시|[panels.py](files/panels.py.md)|
|`README.md`|사용 안내|[README.md](files/README.md.md)|
|`render.py`|화면 조립|[render.py](files/render.py.md)|
|`requirements.txt`|실행 의존성|[requirements.txt](files/requirements.txt.md)|
|`state.py`|확정 게임 상태|[state.py](files/state.py.md)|
|`test_actions_client.py`|회귀 검증|[test_actions_client.py](files/test_actions_client.py.md)|
|`test_delivery_client.py`|회귀 검증|[test_delivery_client.py](files/test_delivery_client.py.md)|
|`test_history_client.py`|회귀 검증|[test_history_client.py](files/test_history_client.py.md)|
|`test_multiplayer.py`|회귀 검증|[test_multiplayer.py](files/test_multiplayer.py.md)|
|`tools/check_routing_docs.py`|문서 검증|[tools/check_routing_docs.py](files/tools/check_routing_docs.py.md)|
|`world.py`|마을 표시|[world.py](files/world.py.md)|

## 확인 순서

1. 수정할 파일 문서에서 시그니처·입출력과 직접 호출을 확인합니다.
2. 필요한 코드만 바꾼 뒤 해당 1:1 문서와 이 색인을 함께 갱신합니다.
3. `python tools/check_routing_docs.py`로 파일·문서·색인·시그니처를 확인합니다.
4. `python -m unittest discover -s . -p "test_*.py" -v`로 게임 상태와 조회 경계를 검사합니다.
5. `python client/main.py --check` 후 기존 서버로 로그인해 행동 통계·이력·이동/채집/X수련을 확인합니다.
6. 작업 전후 차이와 검증 범위는 [확인 기록](verification/README.md)에서 읽습니다.
