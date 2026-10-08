# 2026-10-07 · 수정23일차3교시를 현재 구조에 연결

> 2026-10-07 검토 주석: 이 문서의 3교시=접속기 구현, False/True=최신 정본 설명은 현재 교안과 다릅니다. 당시 변경·검증 이력으로 보존하며 현재 수업 안내로 사용하지 않습니다. [차이와 현재 상태](../../../ad_server/docs/server-routing/reviews/2026-10-07-lesson-deviations.md).

## 목적·결과

교안과 현재 코드 구조가 달라3교시 진행 방법이 불명확하다는 요청에 맞춰 기존계층 대응표와 실행순서를 작성했다. 최신정본은 Desktop의 「현재 ad_server에서 노출·클릭과 광고주 보고서 완성하기.html」 v2.3이다. 표시→노출→확인뒤클릭의 기존 흐름에 새교안의 영구오류 중지·2초새선택·503클릭재시도·표시후10초유지를 적용했다. 새기초파일은CODE28 그대로이며 False/True를출력한다.

## 작업 시작 Git 상태

직전커밋: 2dd8d97 22일차 내용 반영. 기존변경은 모두작업시작전에존재한변경으로취급하고 먼저읽고문서정합성을검사했다.

### 기존 staged

```text
없음
```

### 기존 unstaged

```text
M	client/app.py
M	client/application/ads.py
M	client/application/controller.py
M	client/contracts/ads.py
M	client/contracts/messages.py
M	client/network/ads.py
M	client/network/session.py
M	client/network/worker.py
M	client/ui/ads.py
M	client/ui/input.py
M	client/ui/renderer.py
M	docs/client-routing/README.md
M	docs/client-routing/files/client/app.py.md
M	docs/client-routing/files/client/application/ads.py.md
M	docs/client-routing/files/client/application/controller.py.md
M	docs/client-routing/files/client/contracts/ads.py.md
M	docs/client-routing/files/client/contracts/messages.py.md
M	docs/client-routing/files/client/network/ads.py.md
M	docs/client-routing/files/client/network/session.py.md
M	docs/client-routing/files/client/network/worker.py.md
M	docs/client-routing/files/client/ui/ads.py.md
M	docs/client-routing/files/client/ui/input.py.md
M	docs/client-routing/files/client/ui/renderer.py.md
```

### 기존 untracked

```text
docs/client-routing/files/tests/test_ads_events.py.md
docs/client-routing/verification/day23-final-audit.json
docs/client-routing/verification/day23-start-audit.json
docs/client-routing/verification/lesson-align-final-audit.json
docs/client-routing/verification/lesson-align-start-audit.json
docs/handoffs/2026-10-07-day22-day23-revised-lesson-alignment.md
docs/handoffs/2026-10-07-day23-period01-02-sync.md
tests/test_ads_events.py
```


공통기록: ad_server/docs/server-routing/verification/day23-period03/start.json, before/, pre-audit.json. env는 해시만 저장하고 실제값을복사하지않았다.

## 이번 변경 파일

- modified: `README.md`
- modified: `client/app.py`
- modified: `client/application/ads.py`
- modified: `client/application/controller.py`
- modified: `client/network/ads.py`
- modified: `client/network/session.py`
- modified: `client/network/http.py`
- modified: `client/contracts/messages.py`
- modified: `client/ui/ads.py`
- modified: `tests/test_ads_events.py`
- modified: `tests/test_ads_feature.py`

파일이동/삭제·Git stage/commit/push는없다. 기존 Game-server 코드는 변경하지 않았다. Game-client에서 기존부터변경됐던 worker/input/renderer/contracts.ads 등도 이번작업에서수정하지않았다. 전체HEAD diff가아닌 start.json/changes.json의시작·최종해시로이번변경을구분한다.

## 책임·교안 대응

- 교안의 messages/ports/ads_panel/controller/network_api/network/client_app/render_ads는 현재 contracts/application/network/ui의기존역할에연결했다. 구체적인파일/함수대응표는 Game-client/README.md:35에있다.
- AdSlot.can_request는15초/실제첫표시후10초/노출응답/진행중사건/미완료실제클릭을검사한다. UI의같은결정decode실패신호는이미지실패새선택을허용하고표시/사건으로세지않는다.
- click_requested는실제마우스요청시에만쓰고503/timeout뒤2초에다음표시프레임에서같은결정을재전송한다. 성공확인뒤클릭은다시보내지않는다.
- AdEventRejected/ProtocolError는400·403·404를영구거절로분류한다. 상태는사건재시도를중지하고2초뒤새선택을허용한다. gateway의현재generation 선택cooldown도같은정책에맞춘다.302/401은기존logout 경로로정리한다.
- HTTP400의공개본문은최대64KiB와세known code로한정한다. 미지정메시지/private trace는사용하지않는다. 기존세션/CSRF/기타HTTP정책은유지한다.
- 3교시공통대상인로그인후village-board만사건을보낸다. 기존lobby카드이미지/금액/ID표시는유지한다. 다운로드/웹조회/빈광고/이미지실패/숨긴패널/최소화는새노출·클릭의증거가아니다.
- 기존verify_day23는새3교시범위로갱신했다. 증거는새day23-period03에기록하고이전period02기록을보존한다.4교시이후NDJSON/집계/일별보고서/전달은미적용이다.

## 라우팅 문서

코드검증뒤별도단계에서이번변경파일의짝만현재시그니처·파라미터·반환·의사코드·호출·상태출처로정합화했다.

- `docs/client-routing/files/README.md.md`
- `docs/client-routing/files/client/app.py.md`
- `docs/client-routing/files/client/application/ads.py.md`
- `docs/client-routing/files/client/application/controller.py.md`
- `docs/client-routing/files/client/network/ads.py.md`
- `docs/client-routing/files/client/network/session.py.md`
- `docs/client-routing/files/client/network/http.py.md`
- `docs/client-routing/files/client/contracts/messages.py.md`
- `docs/client-routing/files/client/ui/ads.py.md`
- `docs/client-routing/files/tests/test_ads_events.py.md`
- `docs/client-routing/files/tests/test_ads_feature.py.md`
- 색인: `docs/client-routing/README.md`

## 검사·결과

- Game-client SDLdummy: `.\.venv\Scripts\python.exe -X utf8 -B -m unittest discover -s tests` →57PASS. 새7개는영구거절/2초새선택,503실제클릭재전송,로비사건없음,decode실패,세션거절분류,공개HTTP오류,networkcooldown을검증한다. 기존유지시간테스트도노출저장확인을추가했다.
- ad_server: `python tools/verify_day23.py --mongod "C:/Program Files/MongoDB/Server/8.3/bin/mongod.exe"` →격리Mongo27109·SQLite·HTTP18000/18001·PNG·SDLdummy/모의click·광고주events연결PASS. 마을impression/click2건,최초시각/당시입찰/createdFalse/확인된클릭미재전송,로비표시를검증한다.
- Game-client `python client/main.py --check` →Python3.12/pygame-ce/aiohttp 설정PASS,서버연결없음. ad config/day23-period-03.py →False/True와교안CODE28 AST일치.
- routing-doc-auditor →클라이언트변경14Python/117symbols 문제0(기존변경포함). tools/check_routing_docs.py →77파일/77짝PASS. 광고nonGit의3개이번변경짝·색인/scoped AST PASS. git diff --check PASS.
- 두서버env의시작·종료해시불변. 실제수업DB·계정·키·Mongo인프라를수정하지않았다.
- 광고nonGit검사에서작업디렉터리중복경로를한번고친뒤올바른Chapter3경계로재검사했다. 최종검사에남은오류는없다.

## 미실행·후속

- 실제학생의Pygame창표시·마우스click/Compass관찰은not_run이다. fixture증거를실수업증거로대체하지않는다.
- 이미켜져있는접속기는기존코드를실행하므로창을닫고재실행해야한다. 두서버는기존8000/8001·게임의기존HTTP/WS운영명령을유지한다.
- 새선택이가능해진뒤에는광고가자동갱신될수있다. 웹은카드와같은결정ID 행을찾는다. 광고주와게임계정은서로다른기존계정을사용한다.
- 상태/구조개편이나추가환경설치·비밀값변경을하지않았다.4교시이후작업은요청된범위밖이다.

## 수업 실행 순서

```powershell
Set-Location C:\MLO01-01\Chapter3\ad_server
.\.venv\Scripts\python.exe config/day23-period-03.py
Set-Location C:\MLO01-01\Chapter3\Game-client
.\.venv\Scripts\python.exe client/main.py
```

게임로그인 → 마을광고노출완료 → 광고주 http://127.0.0.1:8001/advertiser/events/의같은결정노출시각 → 실제광고이미지/카드click → 클릭완료/같은행클릭시각. 새로보기버튼은광고click이아니다. 상세파일대응표는Game-client README의3교시항목이다.

테스트용SDL_VIDEODRIVER/SDL_AUDIODRIVER=dummy가남았다면README의Remove-Item Env:... 두명령으로지운뒤게임을실행한다. 실제창관찰이끝나면same decision ID·노출/클릭시각을수업증거로직접기록한다.
