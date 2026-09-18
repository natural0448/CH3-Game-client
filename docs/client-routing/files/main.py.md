# main.py

## 계층과 책임

진입·조립 — 명령행 검사 후 configuration과 app을 연결한다. UI 세부나 HTTP 내부를 알지 않는다.

원문: `Game-client/main.py`. 호출 경계는 아래 직접 의존성까지만 기술합니다.

## 직접 의존성

```text
from app import run
from configuration import load_config
from importlib.metadata import version
from network import NetworkWorker
import argparse
import os
import sys
```

## 변수·상수와 출처

인스턴스/지역 변수는 각 함수 의사코드의 설정식이 출처입니다. 필드 갱신은 해당 메서드 항목에만 기록합니다.

```text
없음
```

## main()

동기 함수: 이 파일의 계층에서 호출한다.

파라미터:
- 없음.

기본값은 시그니처에 기재합니다. `self`는 호출 객체이며 반환값은 아래 `반환` 지점에 기재합니다. 명시적 반환이 없으면 None입니다.

내부 동작 (의사코드):

```text
설정 parser ← argparse.ArgumentParser(description='작은 마을 Pygame 접속기')
실행 parser.add_argument('--check', action='store_true', help='설정과 의존성만 확인 (서버 연결 없음)')
설정 args ← parser.parse_args()
조건 sys.version_info[:2] != (3, 12) 이면:
  실행 print('Python 3.12 환경에서 실행해 주세요.')
  반환 1
설정 config ← load_config()
조건 args.check 이면:
  실행 NetworkWorker(config)
  의존성 가져오기 from importlib.metadata import version
  실행 print(f"Python 3.12 | pygame-ce {version('pygame-ce')} | aiohttp {version('aiohttp')}")
  실행 print('Config OK. No server connection was opened.')
  반환 0
의존성 가져오기 from app import run
반환 run(config)
```

직접 호출 (내부 구현을 펼치지 않음):

```text
NetworkWorker
argparse.ArgumentParser
load_config
parser.add_argument
parser.parse_args
print
run
version
```
