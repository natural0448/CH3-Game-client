# client/contracts/queries.py

## 책임과 상수

읽기 전용 API의 고정 경로·미생성 문구·parser를 정의한다. `ACTION_TYPES`는 moved/gathered/trained 세 종류다. `QUERY_SPECS`는 delivery, analytics, actions, ingest, windows, load, metrics, history만 허용하고 delivery의 최소 간격은 5초다. 18일차 snapshot 경로는 `/api/analytics/load/`와 `/api/analytics/metrics/`다.

## 함수

`_count(value)` — bool을 제외한 0 이상 int를 반환한다.

`_text(value, limit=128)` — 출력 가능한 1..limit 문자열을 반환한다.

`read_delivery(data)` — event_count, pending_publish_count, `source='mysql-outbox'`만 복사한다.

`read_analytics(data)`

```text
available bool 검사; false이면 숫자 필드를 만들지 않고 available=false만 반환
true이면 schema_version=1과 timezone 포함 generated_at 검사
source는 raw 또는 delta만 허용
event_count를 0 이상 정수로 복사
record_count가 존재하고 null이 아닐 때만 0 이상 정수로 복사
by_action[event_type,count]와 by_room[room_id,count]의 허용 필드만 복사
알 수 없는 필드와 인증 관련 값은 버림
```

`read_actions(data)`

```text
available bool 검사; false면 summary=None
source_topic=game.actions.v1, source_kind=bounded-kafka-snapshot 검사
generated_at·고유 event_count·세 action label/count·방별 count 검사
raw_record_count와 선택 bounds/label_source만 복사
```

`read_ingest(data)`

```text
available bool 검사
false면 알려진 reason만 복사하고 숫자 필드는 만들지 않음
true면 schema_version=1, source=kafka-parquet, timezone 포함 generated_at 검사
record_count/event_count/duplicate_record_count와 세 행동의 event_type/count만 복사
고유 사건·중복·행동 합의 관계를 검사
```

`read_windows(data)`

```text
available bool 검사; false이면 숫자를 만들지 않고 빈 windows만 반환
true이면 timezone이 있는 generated_at과 최대 40개 windows 검사
각 행의 kind가 tumbling/sliding인지, 시작·끝이 timezone 포함 시각이고 끝이 뒤인지 검사
ACTION_TYPES의 event_type과 0 이상 count만 허용 목록으로 복사
세션이나 알 수 없는 응답 필드는 버림
```

`_number(value, *, optional=False)` — bool을 제외한 0 이상 int/float를 검사하며 optional일 때만 `None`을 허용한다.

`_timestamp(value)` — 출력 가능한 짧은 문자열이며 timezone을 가진 ISO 시각인지 검사한다.

`read_load(data)`

```text
available=false이면 숫자를 만들지 않고 load=None 유지
true이면 생성·측정 시작 시각과 profile의 입력 조건 검사
연결·요청·성공·오류·경과·처리율과 nullable RTT 검사
by_room의 room_id/connected/success_count만 최대 20행 복사
서버의 계정별 행과 알 수 없는 필드는 버림
```

`read_metrics(data)`

```text
available=false이면 숫자를 만들지 않고 metrics=None 유지
true이면 schema version과 지표 생성·구간 시각, DB count 검사
행동·방별 작은 목록의 허용 필드만 복사
Kafka topic/group/partition 위치와 nullable committed/lag, lag_complete 검사
Spark progress가 있으면 식별자·기록 시각·batch·처리량만 복사
```

`QuerySpec` 변수는 `path`, `empty_message`, `parser`, `minimum_interval`을 갖는다. 직접 호출: `datetime.fromisoformat`, `read_history`, 내장 타입 검사.
