# client/contracts/messages.py

## 책임과 타입

queue 경계의 `NetworkRequest`, `NetworkEvent`를 `dict[str, Any]` TypeAlias로 정의한다. Surface·세션·쿠키 객체는 이 타입에 넣지 않는다. 함수 호출은 없다.
