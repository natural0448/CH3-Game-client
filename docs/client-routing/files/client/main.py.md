# client/main.py

## 계층과 책임

호환 진입 — 교안 실행 경로를 기존 main.py에 위임한다. 별도 게임·설정·세션을 만들지 않는다.

원문: `Game-client/client/main.py`. 호출 경계는 아래 직접 의존성까지만 기술합니다.

## 직접 의존성

```text
from pathlib import Path
import runpy
import sys
```

## 변수·상수와 출처

인스턴스/지역 변수는 각 함수 의사코드의 설정식이 출처입니다. 필드 갱신은 해당 메서드 항목에만 기록합니다.

```text
설정 ROOT ← Path(__file__).resolve().parent.parent
```
