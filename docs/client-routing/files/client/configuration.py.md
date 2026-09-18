# client/configuration.py

## 책임과 값 출처

프로젝트 루트 `config.json`을 읽고 표시 설정을 검증한다. 인증 정보는 읽지 않는다.

## 함수

`load_config()`

```text
Path(__file__).parent.parent/config.json을 UTF-8 JSON으로 읽음
tile_size=32 확인
window_width·window_height·fps의 정수 범위 확인
검증된 dict 반환
```

직접 호출: `Path.read_text`, `json.loads`.
