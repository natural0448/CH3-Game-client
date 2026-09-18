# 클라이언트 라우팅 지도

읽기 순서: 이 색인 → 관련 파일 문서 → 필요한 코드. 전체 저장소를 먼저 읽지 않는다.

[최종 계층화 실행 계획](layering-plan.md)은 현재 코드에 반영된 책임 경계와 적용 기준이다. 각 파일의 실제 시그니처·파라미터·값 출처·의사코드·직접 호출은 `files/<개발 루트 상대경로>.md`에서 읽는다.

## 계층과 호출 방향

```text
client/main.py → configuration.load_config → client.app.run
client.app → Controller / NetworkWorker / InputRouter / ScreenRenderer
Controller → NetworkPort / GameState / QueryStore
NetworkWorker → AuthSession / PlayChannel / QueryGateway
AuthSession·QueryGateway → JsonHttpClient → 기존 aiohttp ClientSession
PlayChannel·QueryGateway → contracts → credential-free result queue
Controller.screen_model → ScreenRenderer → sections/world/panels/overlays
```

- network는 model·UI·Pygame을 import하지 않는다.
- model은 application·network·UI를 import하지 않는다.
- UI는 aiohttp와 network를 import하지 않는다.
- worker는 하나의 thread, loop, ClientSession을 사용한다.
- Pygame event/draw/image/font/display는 메인 스레드에서만 실행한다.
- `/api/analytics/actions/`는 사용자가 버튼을 누를 때만 GET하며 Spark 실행이나 Kafka 연결을 하지 않는다.

## 수정 위치 빠른 선택

|작업|먼저 읽을 문서|
|---|---|
|프레임·종료|[client/app.py](files/client/app.py.md)|
|사용자 의도·결과 전달|[client/application/controller.py](files/client/application/controller.py.md)|
|서버 확정 상태|[client/model/game.py](files/client/model/game.py.md)|
|HTTP 정책·인증|[client/network/http.py](files/client/network/http.py.md) → [session.py](files/client/network/session.py.md)|
|WebSocket·재연결|[client/network/play.py](files/client/network/play.py.md)|
|읽기 전용 GET|[client/network/queries.py](files/client/network/queries.py.md) → [contracts/queries.py](files/client/contracts/queries.py.md)|
|입력·좌표|[client/ui/input.py](files/client/ui/input.py.md) → [layout.py](files/client/ui/layout.py.md)|
|화면 합성|[client/ui/renderer.py](files/client/ui/renderer.py.md)|
|행동 통계 표시|[client/ui/panels.py](files/client/ui/panels.py.md)|
|마을·캐릭터 이름|[client/ui/world/scene.py](files/client/ui/world/scene.py.md) → [projection.py](files/client/ui/world/projection.py.md)|

## 파일별 1:1 색인

|개발 파일|책임|짝 문서|
|---|---|---|
|`.gitignore`|관리 제외|[.gitignore](files/.gitignore.md)|
|`README.md`|실행·구조 안내|[README.md](files/README.md.md)|
|`main.py`|루트 호환 진입|[main.py](files/main.py.md)|
|`config.json`|로컬 설정|[config.json](files/config.json.md)|
|`requirements.txt`|Python 의존성|[requirements.txt](files/requirements.txt.md)|
|`client/__init__.py`|package 경계|[client/__init__.py](files/client/__init__.py.md)|
|`client/main.py`|실행 진입|[client/main.py](files/client/main.py.md)|
|`client/configuration.py`|설정 검증|[client/configuration.py](files/client/configuration.py.md)|
|`client/app.py`|객체 조립·프레임 수명|[client/app.py](files/client/app.py.md)|
|`client/application/__init__.py`|package 경계|[client/application/__init__.py](files/client/application/__init__.py.md)|
|`client/application/controller.py`|intent·event 조정|[client/application/controller.py](files/client/application/controller.py.md)|
|`client/application/queries.py`|조회 상관관계|[client/application/queries.py](files/client/application/queries.py.md)|
|`client/application/state.py`|화면 상태·불변 표시 DTO|[client/application/state.py](files/client/application/state.py.md)|
|`client/model/__init__.py`|package 경계|[client/model/__init__.py](files/client/model/__init__.py.md)|
|`client/model/game.py`|서버 확정 게임 상태|[client/model/game.py](files/client/model/game.py.md)|
|`client/contracts/__init__.py`|package 경계|[client/contracts/__init__.py](files/client/contracts/__init__.py.md)|
|`client/contracts/auth.py`|인증 응답 계약|[client/contracts/auth.py](files/client/contracts/auth.py.md)|
|`client/contracts/game.py`|게임 wire 계약|[client/contracts/game.py](files/client/contracts/game.py.md)|
|`client/contracts/history.py`|개인 이력 계약|[client/contracts/history.py](files/client/contracts/history.py.md)|
|`client/contracts/messages.py`|queue 타입|[client/contracts/messages.py](files/client/contracts/messages.py.md)|
|`client/contracts/queries.py`|읽기 API 계약|[client/contracts/queries.py](files/client/contracts/queries.py.md)|
|`client/network/__init__.py`|NetworkWorker 공개|[client/network/__init__.py](files/client/network/__init__.py.md)|
|`client/network/port.py`|application port|[client/network/port.py](files/client/network/port.py.md)|
|`client/network/worker.py`|thread·loop·dispatch|[client/network/worker.py](files/client/network/worker.py.md)|
|`client/network/http.py`|JSON HTTP 정책|[client/network/http.py](files/client/network/http.py.md)|
|`client/network/session.py`|인증 session·CSRF|[client/network/session.py](files/client/network/session.py.md)|
|`client/network/play.py`|WebSocket·재연결|[client/network/play.py](files/client/network/play.py.md)|
|`client/network/queries.py`|버튼형 GET 작업|[client/network/queries.py](files/client/network/queries.py.md)|
|`client/ui/__init__.py`|package 경계|[client/ui/__init__.py](files/client/ui/__init__.py.md)|
|`client/ui/input.py`|Pygame event→intent|[client/ui/input.py](files/client/ui/input.py.md)|
|`client/ui/layout.py`|draw/hit geometry|[client/ui/layout.py](files/client/ui/layout.py.md)|
|`client/ui/assets.py`|font/image cache|[client/ui/assets.py](files/client/ui/assets.py.md)|
|`client/ui/drawing.py`|그리기 primitive|[client/ui/drawing.py](files/client/ui/drawing.py.md)|
|`client/ui/renderer.py`|화면 합성|[client/ui/renderer.py](files/client/ui/renderer.py.md)|
|`client/ui/panels.py`|조회 패널·API 텍스트|[client/ui/panels.py](files/client/ui/panels.py.md)|
|`client/ui/overlays.py`|연결·상태 overlay|[client/ui/overlays.py](files/client/ui/overlays.py.md)|
|`client/ui/sections/__init__.py`|package 경계|[client/ui/sections/__init__.py](files/client/ui/sections/__init__.py.md)|
|`client/ui/sections/header.py`|제목·연결 요약|[client/ui/sections/header.py](files/client/ui/sections/header.py.md)|
|`client/ui/sections/account.py`|로그인 표시|[client/ui/sections/account.py](files/client/ui/sections/account.py.md)|
|`client/ui/sections/commands.py`|확정 상태·명령 버튼|[client/ui/sections/commands.py](files/client/ui/sections/commands.py.md)|
|`client/ui/sections/activity.py`|방·WS·API 표시|[client/ui/sections/activity.py](files/client/ui/sections/activity.py.md)|
|`client/ui/sections/lobby.py`|조회 진입·광고 slot|[client/ui/sections/lobby.py](files/client/ui/sections/lobby.py.md)|
|`client/ui/world/__init__.py`|package 경계|[client/ui/world/__init__.py](files/client/ui/world/__init__.py.md)|
|`client/ui/world/scene.py`|world layer 순서|[client/ui/world/scene.py](files/client/ui/world/scene.py.md)|
|`client/ui/world/projection.py`|player 표시 DTO|[client/ui/world/projection.py](files/client/ui/world/projection.py.md)|
|`client/ui/world/terrain.py`|지형·장식|[client/ui/world/terrain.py](files/client/ui/world/terrain.py.md)|
|`client/ui/world/markers.py`|채집·수련 marker|[client/ui/world/markers.py](files/client/ui/world/markers.py.md)|
|`client/ui/world/actors.py`|캐릭터 layer|[client/ui/world/actors.py](files/client/ui/world/actors.py.md)|
|`client/ui/world/nameplates.py`|player 이름표|[client/ui/world/nameplates.py](files/client/ui/world/nameplates.py.md)|
|`tests/__init__.py`|테스트 package|[tests/__init__.py](files/tests/__init__.py.md)|
|`tests/support.py`|공통 fake·fixture|[tests/support.py](files/tests/support.py.md)|
|`tests/test_game_state.py`|게임 상태 회귀|[tests/test_game_state.py](files/tests/test_game_state.py.md)|
|`tests/test_actions_contract.py`|행동 응답 계약|[tests/test_actions_contract.py](files/tests/test_actions_contract.py.md)|
|`tests/test_network_queries.py`|HTTP·조회 회귀|[tests/test_network_queries.py](files/tests/test_network_queries.py.md)|
|`tests/test_actions_ui.py`|행동 패널·Layout 회귀|[tests/test_actions_ui.py](files/tests/test_actions_ui.py.md)|
|`tools/check_routing_docs.py`|문서 정합성 검사|[tools/check_routing_docs.py](files/tools/check_routing_docs.py.md)|
|`assets/README.md`|에셋 출처|[assets/README.md](files/assets/README.md.md)|
|`assets/grass.png`|CC0 이미지|[assets/grass.png](files/assets/grass.png.md)|
|`assets/path.png`|CC0 이미지|[assets/path.png](files/assets/path.png.md)|
|`assets/tree.png`|CC0 이미지|[assets/tree.png](files/assets/tree.png.md)|
|`assets/house.png`|CC0 이미지|[assets/house.png](files/assets/house.png.md)|
|`assets/hero.png`|CC0 이미지|[assets/hero.png](files/assets/hero.png.md)|
|`assets/fonts/LICENSE`|font license|[assets/fonts/LICENSE](files/assets/fonts/LICENSE.md)|
|`assets/fonts/NotoSansCJKkr-Regular.otf`|font binary|[assets/fonts/NotoSansCJKkr-Regular.otf](files/assets/fonts/NotoSansCJKkr-Regular.otf.md)|
|`assets/sources/dungeon-License.txt`|source license|[assets/sources/dungeon-License.txt](files/assets/sources/dungeon-License.txt.md)|
|`assets/sources/kenney_tiny-dungeon.zip`|source archive|[assets/sources/kenney_tiny-dungeon.zip](files/assets/sources/kenney_tiny-dungeon.zip.md)|
|`assets/sources/kenney_tiny-town.zip`|source archive|[assets/sources/kenney_tiny-town.zip](files/assets/sources/kenney_tiny-town.zip.md)|
|`assets/sources/town-License.txt`|source license|[assets/sources/town-License.txt](files/assets/sources/town-License.txt.md)|

## 확인 순서

1. 변경할 파일의 짝 문서에서 책임과 직접 호출을 확인한다.
2. 코드 변경 후 해당 1:1 문서와 이 색인만 갱신한다.
3. `python tools/check_routing_docs.py`를 실행한다.
4. `python -m unittest discover -s tests -p "test_*.py" -v`를 실행한다.
5. `python client/main.py --check`로 서버 연결 없이 진입 설정을 확인한다.
6. 실제 서버를 켠 경우 로그인→첫 state→이동·채집·X수련→조회→로그아웃→창 종료를 확인한다.
