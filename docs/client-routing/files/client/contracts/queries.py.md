# client/contracts/queries.py

## 책임과 상수

읽기 전용 API의 고정 경로·미생성 문구·parser를 정의한다. `ACTION_TYPES`는 moved/gathered/trained 세 종류다. `QUERY_SPECS`는 delivery, analytics, actions, ingest, windows, load, metrics, lake, history만 허용하고 delivery의 최소 간격은 5초다. Lake 경로는 `/api/analytics/lake/`, parser는 `read_lake`, 최소 간격은 기본 0초(동시 요청은 상위 계층에서 차단)다.

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

## 원본 보존 응답

`read_lake(data)` — data는 worker가 읽은 JSON 사전이며 반환값은 새 허용 필드 사전이다. 잘못된 타입·필수 필드·시각·검사 범위는 ValueError로 거절한다.

```text
schema_version이 bool이 아닌 정수 1인지 검사
status가 ready/pending/unavailable인지 검사
result에 schema_version/status와 ready일 때만 True인 내부 available 저장
pending/unavailable이면 숫자·matched·서버 message를 복사하지 않고 반환
ready이면 matched가 bool, verification_scope가 local-and-copied-bytes인지 검사
dataset_version은 최대 128자의 출력 가능한 문자열
rows/bytes는 bool이 아닌 0 이상 int
captured_at/generated_at은 timezone을 가진 최대 64자의 ISO 문자열
이 여덟 공개 필드만 result에 추가하고 반환
```

직접 호출은 `_text`, `_count`, `_timestamp`다. 원본 events, player_id 목록, 인증 정보 및 알 수 없는 응답 필드는 복사하지 않는다. `available`은 기존 조회 계층이 사용하는 내부 표시 값이며 새 서버 API 요구 필드가 아니다.

## 부하·운영 응답 (계속)

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
