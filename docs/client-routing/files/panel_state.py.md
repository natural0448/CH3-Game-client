# panel_state.py

## 계층과 책임

조회 패널 상태 — request_id/player_id로 응답을 연결하고 열림·조회 중·페이지를 관리한다. HTTP나 Pygame을 호출하지 않는다.

원문: `Game-client/panel_state.py`. 호출 경계는 아래 직접 의존성까지만 기술합니다.

## 직접 의존성

```text
from dataclasses import dataclass
import uuid
```

## 변수·상수와 출처

인스턴스/지역 변수는 각 함수 의사코드의 설정식이 출처입니다. 필드 갱신은 해당 메서드 항목에만 기록합니다.

```text
클래스 QueryPanel / 기반 없음
  설정 kind ← 'analytics'
  설정 opened ← False
  설정 busy ← False
  설정 response ← None
  설정 pending ← None
  설정 page ← 0
```

## QueryPanel.reset(self)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 self.opened, self.busy ← False
설정 self.response, self.pending ← None
설정 self.page ← 0
```

직접 호출 (내부 구현을 펼치지 않음):

```text
없음
```

## QueryPanel.request(self, state)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.
- `state`: 메인 스레드의 VillageState; 서버 확정 정보만 포함.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
조건 self.busy or state.own is None or state.phase in ('logging_out', 'signed_out', 'stopped') 이면:
  반환 None
설정 self.opened, self.busy ← True
설정 self.pending ← str(uuid.uuid4())
설정 self.page ← 0
설정 self.response ← None
반환 {'kind': self.kind, 'request_id': self.pending, 'player_id': state.own['player_id']}
```

직접 호출 (내부 구현을 펼치지 않음):

```text
str
uuid.uuid4
```

## QueryPanel.accept(self, event, state)

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- `self`: 현재 클래스 인스턴스; 생성자 또는 dataclass 기본값에서 초기화.
- `event`: network 결과 큐에서 app이 전달한 dict.
- `state`: 메인 스레드의 VillageState; 서버 확정 정보만 포함.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
조건 event.get('kind') in ('logged_out', 'login_failed', 'stopped') 이면:
  실행 self.reset()
그 외:
  조건 event.get('kind') == self.kind and self.pending is not None and (event.get('request_id') == self.pending) and (state.own is not None) and (event.get('player_id') == state.own['player_id']) and (state.phase != 'logging_out') 이면:
    설정 self.response ← {key: event[key] for key in ('path', 'status', 'json', 'message')}
    설정 self.busy ← False
    설정 self.pending ← None
```

직접 호출 (내부 구현을 펼치지 않음):

```text
event.get
self.reset
```
