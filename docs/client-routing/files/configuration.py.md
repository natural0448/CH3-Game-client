# configuration.py

## 계층과 책임

설정 — config.json에서 화면 설정을 읽고 범위를 검증한다. 인증 정보를 취급하지 않는다.

원문: `Game-client/configuration.py`. 호출 경계는 아래 직접 의존성까지만 기술합니다.

## 직접 의존성

```text
from pathlib import Path
import json
```

## 변수·상수와 출처

인스턴스/지역 변수는 각 함수 의사코드의 설정식이 출처입니다. 필드 갱신은 해당 메서드 항목에만 기록합니다.

```text
없음
```

## load_config()

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- 없음.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 path ← Path(__file__).resolve().with_name('config.json')
설정 config ← json.loads(path.read_text(encoding='utf-8'))
조건 config.get('tile_size', 32) != 32 이면:
  실패 전달 ValueError('The server map uses logical tiles of 32 pixels')
반복 (key, low, high) ← (('window_width', 640, 3840), ('window_height', 480, 2160), ('fps', 30, 120)):
  설정 value ← config.get(key)
  조건 type(value) is not int or not low <= value <= high 이면:
    실패 전달 ValueError(f'Invalid config value: {key}')
반환 config
```

직접 호출 (내부 구현을 펼치지 않음):

```text
Path
Path(__file__).resolve
Path(__file__).resolve().with_name
ValueError
config.get
json.loads
path.read_text
type
```
