# config.json

## 계층과 책임

설정 데이터 — 네트워크 주소·timeout·화면 크기·에셋 경로의 기본값이다. 비밀번호·쿠키·CSRF를 저장하지 않는다.

원문: `Game-client/config.json`. 호출 경계는 아래 직접 의존성까지만 기술합니다.

## 값과 출처

```text
{
  "server_base_url": "http://127.0.0.1:8000",
  "http_timeout_seconds": 8,
  "command_timeout_seconds": 8,
  "window_width": 1100,
  "window_height": 880,
  "fps": 60,
  "tile_size": 32,
  "assets_dir": "assets",
  "font_path": "fonts/NotoSansCJKkr-Regular.otf"
}
```

## 호출과 시그니처

함수·메서드 없음. 데이터/설명 파일이며 코드처럼 실행하지 않습니다.
