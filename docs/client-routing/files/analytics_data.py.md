# analytics_data.py

## 계층과 책임

응답 검증 — 집계 계약을 검사하고 표시 허용 필드만 새 dict로 복사한다. Player 상태나 HTTP를 알지 않는다.

원문: `Game-client/analytics_data.py`. 호출 경계는 아래 직접 의존성까지만 기술합니다.

## 직접 의존성

```text
from datetime import datetime
```

## 변수·상수와 출처

인스턴스/지역 변수는 각 함수 의사코드의 설정식이 출처입니다. 필드 갱신은 해당 메서드 항목에만 기록합니다.

```text
설정 API_RESPONSE_FIELDS ← {'/api/analytics/actions/': ('available', 'source_topic', 'source_kind', 'raw_record_count', 'bounds', 'label_source', 'summary'), '/api/history/': ('scope', 'limit', 'events'), '/api/delivery/': ('event_count', 'pending_publish_count', 'source'), '/api/analytics/': ('available', 'schema_version', 'generated_at', 'event_count', 'by_action', 'by_room')}
설정 ACTION_TYPES ← ('player.moved', 'player.gathered', 'player.trained')
```

## read_analytics(data)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `data`: 호출자가 전달한 JSON 객체; 이 함수가 허용 필드를 검증.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
조건 type(data.get('available')) is not bool 이면:
  실패 전달 ValueError('invalid_analytics')
조건 not data['available'] 이면:
  반환 {'available': False}
조건 type(data.get('schema_version')) is not int or data['schema_version'] != 1 이면:
  실패 전달 ValueError('invalid_analytics')
조건 type(data.get('event_count')) is not int or data['event_count'] < 0 이면:
  실패 전달 ValueError('invalid_analytics')
설정 timestamp ← data.get('generated_at')
조건 not isinstance(timestamp, str) or len(timestamp) > 64 or datetime.fromisoformat(timestamp).tzinfo is None 이면:
  실패 전달 ValueError('invalid_analytics')
설정 safe ← {key: data[key] for key in ('available', 'schema_version', 'generated_at', 'event_count')}
반복 (field, key) ← (('by_action', 'event_type'), ('by_room', 'room_id')):
  설정 rows ← data.get(field)
  조건 not isinstance(rows, list) or len(rows) > 100 이면:
    실패 전달 ValueError('invalid_analytics')
  설정 safe[field] ← []
  반복 row ← rows:
    조건 not isinstance(row, dict) or not isinstance(row.get(key), str) or (not 1 <= len(row[key]) <= 128) or (not row[key].isprintable()) or (type(row.get('count')) is not int) or (row['count'] < 0) 이면:
      실패 전달 ValueError('invalid_analytics')
    실행 safe[field].append({key: row[key], 'count': row['count']})
반환 {key: safe[key] for key in API_RESPONSE_FIELDS['/api/analytics/']}
```

직접 호출 (내부 구현을 펼치지 않음):

```text
ValueError
data.get
datetime.fromisoformat
isinstance
len
row.get
row[key].isprintable
safe[field].append
type
```

## _count(value)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `value`: 호출자가 전달하는 `value`; 값의 사용과 직접 호출 출처는 아래 의사코드에 표시.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
조건 type(value) is not int or value < 0 이면:
  실패 전달 ValueError('invalid_action_count')
반환 value
```

직접 호출 (내부 구현을 펼치지 않음):

```text
ValueError
type
```

## _text(value, limit=128)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `value`: 호출자가 전달하는 `value`; 값의 사용과 직접 호출 출처는 아래 의사코드에 표시.
- `limit`: 호출자가 전달하는 `limit`; 값의 사용과 직접 호출 출처는 아래 의사코드에 표시.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
조건 not isinstance(value, str) or not 1 <= len(value) <= limit or (not value.isprintable()) 이면:
  실패 전달 ValueError('invalid_action_text')
반환 value
```

직접 호출 (내부 구현을 펼치지 않음):

```text
ValueError
isinstance
len
value.isprintable
```

## read_actions(data)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `data`: 호출자가 전달한 JSON 객체; 이 함수가 허용 필드를 검증.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
조건 not isinstance(data, dict) or type(data.get('available')) is not bool 이면:
  실패 전달 ValueError('invalid_actions')
조건 not data['available'] 이면:
  반환 {'available': False, 'summary': None}
조건 data.get('source_topic') != 'game.actions.v1' or data.get('source_kind') != 'bounded-kafka-snapshot' 이면:
  실패 전달 ValueError('invalid_action_source')
설정 summary ← data.get('summary')
조건 not isinstance(summary, dict) 이면:
  실패 전달 ValueError('invalid_action_summary')
설정 stamp ← _text(summary.get('generated_at'), 64)
조건 datetime.fromisoformat(stamp).tzinfo is None 이면:
  실패 전달 ValueError('invalid_action_time')
설정 clean ← {'generated_at': stamp, 'event_count': _count(summary.get('event_count'))}
반복 (field, key, limit) ← (('by_action', 'event_type', 3), ('by_room', 'room_id', 100)):
  설정 rows ← summary.get(field)
  조건 not isinstance(rows, list) or len(rows) > limit 이면:
    실패 전달 ValueError('invalid_action_rows')
  설정 clean[field] ← []
  설정 seen ← set()
  반복 row ← rows:
    조건 not isinstance(row, dict) 이면:
      실패 전달 ValueError('invalid_action_row')
    설정 name ← _text(row.get(key))
    조건 name in seen or (field == 'by_action' and name not in ACTION_TYPES) 이면:
      실패 전달 ValueError('invalid_action_row_key')
    실행 seen.add(name)
    설정 item ← {key: name, 'count': _count(row.get('count'))}
    조건 field == 'by_action' 이면:
      설정 item['action_label'] ← _text(row.get('action_label'), 64)
    실행 clean[field].append(item)
설정 result ← {'available': True, 'source_topic': data['source_topic'], 'source_kind': data['source_kind'], 'summary': clean, 'raw_record_count': _count(data.get('raw_record_count'))}
조건 'label_source' in data 이면:
  조건 data['label_source'] != 'current-display-map' 이면:
    실패 전달 ValueError('invalid_label_source')
  설정 result['label_source'] ← data['label_source']
조건 'bounds' in data 이면:
  조건 not isinstance(data['bounds'], list) or len(data['bounds']) > 100 이면:
    실패 전달 ValueError('invalid_bounds')
  설정 result['bounds'] ← []
  반복 row ← data['bounds']:
    조건 not isinstance(row, dict) 이면:
      실패 전달 ValueError('invalid_bounds')
    설정 bound ← {key: _count(row.get(key)) for key in ('partition', 'start_inclusive', 'end_exclusive')}
    조건 bound['start_inclusive'] > bound['end_exclusive'] 이면:
      실패 전달 ValueError('invalid_bounds')
    실행 result['bounds'].append(bound)
반환 result
```

직접 호출 (내부 구현을 펼치지 않음):

```text
ValueError
_count
_text
clean[field].append
data.get
datetime.fromisoformat
isinstance
len
result['bounds'].append
row.get
seen.add
set
summary.get
type
```
