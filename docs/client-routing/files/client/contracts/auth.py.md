# client/contracts/auth.py

## 책임과 변수

인증 응답의 공개 값만 검증한다. frozen `Identity`는 `player_id`, `room_id`, `version`, 검증된 state를 가진다.

## 함수

`read_csrf(data)` — `csrfToken` 또는 `csrf_token`의 1..256 문자열을 반환하며 아니면 `ValueError`다.

`read_login(data)` — object JSON의 `authenticated is True`만 허용한다.

직접 호출: dict 조회와 타입/길이 검사. 토큰은 UI event로 반환하지 않는다.
