# client/contracts/queries.py

## 책임과 상수

읽기 전용 API의 고정 경로·미생성 문구·parser를 정의한다. `ACTION_TYPES`는 moved/gathered/trained 세 종류다. `QUERY_SPECS`는 delivery, analytics, actions, ingest, windows, history만 허용하고 delivery의 최소 간격은 5초다. 시간 창 경로는 `/api/analytics/windows/`다.

## 함수

`_count(value)` — bool을 제외한 0 이상 int를 반환한다.

`_text(value, limit=128)` — 출력 가능한 1..limit 문자열을 반환한다.

`read_delivery(data)` — event_count, pending_publish_count, `source='mysql-outbox'`만 복사한다.

`read_analytics(data)` — available=false를 미생성으로 유지하고 true일 때 schema/time/event_count/by_action/by_room을 검증한다.

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

`QuerySpec` 변수는 `path`, `empty_message`, `parser`, `minimum_interval`을 갖는다. 직접 호출: `datetime.fromisoformat`, `read_history`, 내장 타입 검사.
