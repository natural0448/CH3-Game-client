# client/ui/layout.py

## 책임과 상수

draw와 hit test가 공유하는 불변 logical Layout이다. `CANVAS=(1100,880)`, control/slot/viewport Rect는 `_controls`와 `build_layout`에서만 생성한다. load·metrics·lake 진입과 각 refresh/close Rect도 같은 control 사전에 있다.

## 함수와 메서드

`_controls()` — 로그인, 명령, 기존 조회, load/metrics/lake 버튼과 패널 refresh/close를 포함한 고정 logical Rect dict를 반환한다. lobby의 둘째 줄에 load/metrics, 셋째 줄에 delivery/lake를 둔다. delivery=(366,758,178,28), lake=(550,758,98,28), lake_refresh=(386,174,134,32), lake_close=(530,174,104,32)다. 다른 slot/ad_slot/world Rect는 유지한다.

`Layout.viewport(self)` — 실제 `screen_size`에 맞춘 letterbox 크기와 offset을 계산한다.

`Layout.to_canvas(self, position)` — 화면 mouse 좌표를 logical canvas 좌표로 변환한다.

`Layout.hit_test(self, position, open_panels)` — 열린 analytics/history/actions/ingest/windows/load/metrics/lake 패널 control을 우선한 뒤 일반 control 이름을 반환한다. lake_ control은 해당 패널이 닫힌 상태의 일반 hit 대상에서 제외한다.

`build_layout(screen_size)` — control, 광고 slot, world/panel Rect가 든 frozen Layout을 만든다.

직접 호출: `pygame.Rect`, 내장 `min/max/int`.
