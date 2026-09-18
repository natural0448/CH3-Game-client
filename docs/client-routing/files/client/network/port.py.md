# client/network/port.py

## 책임

application이 볼 수 있는 network Protocol이다. queue에는 JSON-like 요청과 결과만 흐른다.

## 메서드 시그니처

```text
NetworkPort.start(self) -> None
NetworkPort.submit(self, request: NetworkRequest) -> bool
NetworkPort.drain_events(self, limit: int=200) -> list[NetworkEvent]
NetworkPort.is_alive(self) -> bool
NetworkPort.stop(self, timeout: float | None=None) -> None
```

`request`는 application intent, `limit`은 한 프레임 최대 결과 수, `timeout`은 선택 join 시간이다. Protocol은 내부 호출을 수행하지 않는다.
