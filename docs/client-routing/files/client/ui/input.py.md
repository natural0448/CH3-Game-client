# client/ui/input.py

## 책임과 상수

Pygame event를 credential-free application intent로 변환한다. `GAME_KEYS`는 방향키, Space 채집, X 수련이다.

## 메서드

`InputRouter.route(self, event, layout, app, queries)`

```text
QUIT/resize/text/key/mouse를 구분
로그인 focus 중 game key를 반환하지 않음
mouse는 같은 frame Layout.hit_test 사용
login/logout/command/query/panel/API intent dict 반환
windows 진입과 windows_refresh는 같은 query intent로 변환
analytics 진입과 analytics_refresh는 같은 analytics query intent로 변환
load/metrics 진입과 각 refresh는 같은 이름의 query intent로 변환
lake 진입과 lake_refresh는 {kind:query, query:lake}로 변환
lake_close는 기존 suffix 규칙에 따라 panel_close intent로 변환
windows_filter_all/tumbling/sliding은 network query가 아닌 panel_filter intent로 변환
network나 상태 쓰기 메서드는 호출하지 않음
```

`event`는 메인 스레드 Pygame event, `app/queries`는 현재 입력과 열린 패널 상태다. 직접 호출: `Layout.hit_test`, 문자열 분리 메서드.

## 23일차 1~2교시 최종 반영

기존 Layout hit-test로 ad_village_refresh/ad_lobby_refresh를 ad_refresh+slot_id intent로 변환한다. UI 입력 계층은 요청이나 상태 변경을 직접 실행하지 않는다. resize/로그인/게임/query 입력 흐름 유지. 활성 Pygame 화면에서 로그인·기존 제어·조회 패널 입력 처리 후, API 보기가 닫혀 있고 조회 패널이 닫혔을 때 Layout.ad_cards hit를 ad_click intent로 반환한다. 새로 보기 버튼은 먼저 처리해 클릭 실적으로 겹치지 않는다.

클래스 계약: `class InputRouter`.

### `InputRouter.route(self, event, layout, app, queries)`

| 파라미터 | 기본값 | 의미·허용 범위 |
|---|---|---|
| self | 없음 | 해당 클래스 인스턴스; 클래스가 소유한 상태에만 쓴다. |
| event | 없음 | public network event; slot/request/player ID 일치해야 수락. |
| layout | 없음 | 동일 draw/hit-test Layout. |
| app | 없음 | 현재 ApplicationState; InputRouter는 focus/text/연결상태만 읽는다. |
| queries | 없음 | QueryStore; 열린 패널·기존 controls를 읽는다. |

반환·실패: 실제 반환식: `None`, `{'kind': 'quit'}`, `{'kind': 'resize', 'size': (max(320, event.w), max(240, event.h))}`, `{'kind': 'text', 'text': event.text}`, `{'kind': 'focus', 'field': None}`, `{'kind': 'command', 'action': self.GAME_KEYS[event.key]}`, `{'kind': 'focus', 'field': 'username'}`, `{'kind': 'focus', 'field': hit}`, `{'kind': 'login'}`, `{'kind': 'logout'}`, `{'kind': 'ad_refresh', 'slot_id': 'village-board' if hit == 'ad_village_refresh' else 'lobby-banner'}`, `{'kind': 'query', 'query': hit}`, `{'kind': 'query', 'query': 'analytics'}`, `{'kind': 'query', 'query': 'actions'}`, `{'kind': 'query', 'query': 'ingest'}`, `{'kind': 'query', 'query': 'windows'}`, `{'kind': 'query', 'query': 'load'}`, `{'kind': 'query', 'query': 'metrics'}`, `{'kind': 'query', 'query': 'lake'}`, `{'kind': 'panel_filter', 'query': 'windows', 'value': hit.removeprefix('windows_filter_')}`, `{'kind': 'panel_close', 'query': hit.removesuffix('_close')}`, `{'kind': 'panel_page', 'query': query, 'step': -1 if operation == 'previous' else 1}`, `{'kind': 'toggle_api'}`, `{'kind': 'api_source'}`, `{'kind': 'api_scroll', 'step': -3 if hit == 'api_up' else 3}`, `{'kind': 'command', 'action': hit}`, `{'kind': 'focus', 'field': field}`, `{'kind': 'backspace'}`, `{'kind': 'ad_click', 'slot_id': name}`.

의사코드: 파일 책임의 현재 입력·소유상태 확인 → 아래 직접 호출 → 상태 또는 결과 전달.

직접 호출: `layout.hit_test`, `hit.startswith`, `hit.endswith`, `hit.rsplit`, `pygame.display.get_active`, `layout.to_canvas`, `layout.ad_cards.items`, `max`, `queries.slots.items`, `hit.removeprefix`, `hit.removesuffix`, `rect.collidepoint`. 기대 결과는 위 반환·상태 변화에 사용한다. 하위 계층 내부 구현은 그 짝 문서를 따른다.
