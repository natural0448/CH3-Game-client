# client/main.py

## 책임과 값 출처

`python client/main.py` 실행 진입점이다. `ROOT`는 이 파일의 부모의 부모이며 package import 경로로만 사용한다. 설정은 `client.configuration.load_config`에서 받는다.

## 함수

`main()`

```text
CLI의 --check를 읽음
Python 3.12인지 확인
load_config 호출
--check이면 NetworkWorker 생성으로 URL·timeout만 검증하고 설치 버전 출력
그 외 client.app.run(config) 반환
```

직접 호출: `argparse.ArgumentParser`, `load_config`, `NetworkWorker`, `importlib.metadata.version`, `client.app.run`.
