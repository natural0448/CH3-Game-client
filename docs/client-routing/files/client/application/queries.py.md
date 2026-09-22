# client/application/queries.py

## 책임과 상태 출처

읽기 전용 API의 요청 상관관계와 화면 상태를 소유한다. 경로·최소 간격은 `contracts.queries.QUERY_SPECS`, 시간은 `time.monotonic`, ID는 `uuid.uuid4`에서 온다.

## 메서드

`QuerySlot`은 `kind`, `opened`, `busy`, `request_id`, `response`, `page`, `filter_value='all'`, `last_requested_at`을 가진다.

`QuerySlot.reset(self) -> None` — opened/busy/request/response/page/필터/시각을 초기화한다.

`QueryStore.can_request(self, kind, *, now=None)` — busy와 `QUERY_SPECS.minimum_interval`을 확인해 현재 버튼 요청 가능 여부를 반환한다.

`QueryStore.request(self, kind, player_id, *, now=None)`

```text
허용 kind·player_id·busy·최소 간격 확인
UUID request_id 생성, busy와 opened 기록
{kind, request_id, player_id} 반환
```

`QueryStore.cancel(self, kind)` — queue 미전달 요청의 busy·ID·시각을 되돌린다.

`QueryStore.accept(self, event, player_id, *, logging_out=False)`

```text
kind/request_id/player_id와 로그아웃 상태 비교
일치할 때 path/status/json/message 허용 필드만 저장하고 True 반환
```

`QueryStore.close_others(self, kind)` — 선택한 조회 외의 상세 패널을 닫는다.

`QueryStore.turn_page(self, kind, step)` — 응답 행 수와 패널별 page 크기로 범위를 제한한다.

`QueryStore.set_filter(self, kind, value) -> bool` — windows에 한해 `all`, `tumbling`, `sliding`을 저장한다. 요청 큐나 network 계층은 호출하지 않는다.

`QueryStore.reset(self)` — 모든 `QuerySlot.reset`을 호출한다.

직접 호출: `QUERY_SPECS`, `time.monotonic`, `uuid.uuid4`, 내장 `len/max/min`.
