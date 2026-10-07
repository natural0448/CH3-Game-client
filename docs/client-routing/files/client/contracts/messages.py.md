# client/contracts/messages.py

## 책임과 타입

queue 경계의 `NetworkRequest`, `NetworkEvent`를 `dict[str, Any]` TypeAlias로 정의한다. Surface·세션·쿠키 객체는 이 타입에 넣지 않는다. 함수 호출은 없다.

## 22일차 이미지 광고 최종 반영

기존 JSON-like 공개 network result 계약에 광고 PNG의 한정된 bytes를 명시한다. credentials/cookie/token은 result queue 금지이며 image decode/font/display는 UI main thread 책임이다. 나머지 TypedDict 계약은 유지한다.
