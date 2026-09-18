# tests/support.py

## 책임과 fixture 출처

테스트 간 공유하는 게임 wire, 조회 응답과 비동기 HTTP fake만 제공한다.

## 함수와 메서드

`player(pid=1, **changes)` — 기본 room-01 state dict에 변경값을 합친다.

`action_snapshot()` — source, 고유 행동 10건, 원본 12행, 세 행동 카드, room-01 fixture를 반환한다.

`ingest_summary()` — kafka-parquet source, 수집 12행, 고유 사건 10건, 재전달 1행과 세 행동별 count fixture를 반환한다. raw_value와 evidence는 포함하지 않는다.

`Response.__init__(self, status=200, content_type='application/json', data=None, raw=None)` — fake status/content/body를 보관한다.

`Response.__aenter__(self)` — 자신을 async context 결과로 반환한다.

`Response.__aexit__(self, *args)` — 종료 side effect 없이 None을 반환한다.

`Response.iter_chunked(self, size)` — body_read를 기록하고 raw bytes를 yield한다.

`Session.__init__(self, response)` — response, calls, closed=false를 저장한다.

`Session.request(self, *args, **kwargs)` — 호출 인자를 기록하고 fake response를 반환한다.

직접 호출: `json.dumps`.
