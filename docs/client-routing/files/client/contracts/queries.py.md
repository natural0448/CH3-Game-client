# client/contracts/queries.py

## 책임과 상수

읽기 전용 API의 고정 경로·미생성 문구·parser를 정의한다. `ACTION_TYPES`는 moved/gathered/trained 세 종류다. `QUERY_SPECS`는 delivery, analytics, actions, history만 허용하고 delivery의 최소 간격은 5초다.

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

`QuerySpec` 변수는 `path`, `empty_message`, `parser`, `minimum_interval`을 갖는다. 직접 호출: `datetime.fromisoformat`, `read_history`, 내장 타입 검사.
