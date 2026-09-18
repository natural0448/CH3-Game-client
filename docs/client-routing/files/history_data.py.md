# history_data.py

## 계층과 책임

응답 검증 — 자기 계정의 이력 계약과 표시 허용 필드를 검증한다. 서버 상태를 변경하지 않는다.

원문: `Game-client/history_data.py`. 호출 경계는 아래 직접 의존성까지만 기술합니다.

## 직접 의존성

```text
from datetime import datetime
from uuid import UUID
```

## 변수·상수와 출처

인스턴스/지역 변수는 각 함수 의사코드의 설정식이 출처입니다. 필드 갱신은 해당 메서드 항목에만 기록합니다.

```text
없음
```

## read_history(data, player_id)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `data`: 호출자가 전달한 JSON 객체; 이 함수가 허용 필드를 검증.
- `player_id`: 로그인한 계정의 worker.identity 또는 state.own에서 얻은 정수.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
조건 data.get('scope') != 'current-player' or type(data.get('limit')) is not int or data['limit'] != 20 이면:
  실패 전달 ValueError('invalid_history')
설정 events ← data.get('events')
조건 not isinstance(events, list) or len(events) > 20 이면:
  실패 전달 ValueError('invalid_history')
설정 safe ← []
반복 event ← events:
  조건 not isinstance(event, dict) or event.get('player_id') != player_id or type(event.get('player_id')) is not int 이면:
    실패 전달 ValueError('invalid_history_owner')
  실행 UUID(event['event_id'])
  조건 type(event.get('schema_version')) is not int or event['schema_version'] != 1 이면:
    실패 전달 ValueError('invalid_history_schema')
  반복 (field, limit) ← (('event_type', 40), ('room_id', 32), ('event_time', 64)):
    조건 not isinstance(event.get(field), str) or not 1 <= len(event[field]) <= limit or (not event[field].isprintable()) 이면:
      실패 전달 ValueError('invalid_history_text')
  조건 datetime.fromisoformat(event['event_time']).tzinfo is None 이면:
    실패 전달 ValueError('invalid_history_time')
  설정 payload ← event['payload']
  설정 clean ← {}
  반복 key ← ('x', 'y', 'coins', 'version'):
    조건 type(payload.get(key)) is not int 이면:
      실패 전달 ValueError('invalid_history_state')
    설정 clean[key] ← payload[key]
  조건 'command_id' in payload 이면:
    설정 clean['command_id'] ← str(UUID(payload['command_id']))
  설정 transition ← payload.get('transition')
  조건 transition is not None 이면:
    설정 item ← {'episode_id': str(UUID(transition['episode_id']))}
    반복 key ← ('step', 'reward'):
      조건 type(transition.get(key)) is not int 이면:
        실패 전달 ValueError('invalid_transition')
      설정 item[key] ← transition[key]
    조건 not 1 <= item['step'] <= 5 이면:
      실패 전달 ValueError('invalid_transition_step')
    반복 key ← ('done', 'terminated', 'truncated'):
      조건 type(transition.get(key)) is not bool 이면:
        실패 전달 ValueError('invalid_transition_flag')
      설정 item[key] ← transition[key]
    조건 transition.get('policy_version') != 'manual-v1' 이면:
      실패 전달 ValueError('invalid_transition_policy')
    설정 item['policy_version'] ← 'manual-v1'
    설정 action ← transition['action']
    조건 action.get('type') not in ('move', 'gather', 'train') 이면:
      실패 전달 ValueError('invalid_transition_action')
    설정 item['action'] ← {'type': action['type']}
    조건 action['type'] == 'move' 이면:
      조건 action.get('direction') not in ('up', 'down', 'left', 'right') 이면:
        실패 전달 ValueError('invalid_transition_direction')
      설정 item['action']['direction'] ← action['direction']
    반복 key ← ('observation', 'next_observation'):
      설정 observation ← transition[key]
      조건 any((type(observation.get(field)) is not int for field in ('x', 'y', 'coins'))) 이면:
        실패 전달 ValueError('invalid_observation')
      설정 item[key] ← {field: observation[field] for field in ('x', 'y', 'coins')}
    설정 clean['transition'] ← item
  실행 safe.append({**{key: event[key] for key in ('schema_version', 'event_id', 'event_type', 'player_id', 'room_id', 'event_time')}, 'payload': clean})
반환 {'scope': 'current-player', 'limit': 20, 'events': safe}
```

직접 호출 (내부 구현을 펼치지 않음):

```text
UUID
ValueError
action.get
any
data.get
datetime.fromisoformat
event.get
event[field].isprintable
isinstance
len
observation.get
payload.get
safe.append
str
transition.get
type
```
