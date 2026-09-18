# client/network/play.py

## 책임과 상태

한 계정의 WebSocket, 최초 state, epoch, own version, wire pending command와 재연결을 소유한다. HTTP 로그인·조회와 UI 상태는 알지 않는다.

## 메서드

`PlayChannel.__init__(self, auth_session, emit, command_timeout)` — 같은 session, queue callback, timeout과 초기 WS 상태를 저장한다.

`PlayChannel.status(self, phase, message)` — 현재 epoch의 credential-free status event를 emit한다.

`PlayChannel.start(self, identity)` — Identity/version을 설정하고 `run` task 한 개를 만든다.

`PlayChannel.close(self)` — 재연결·receive task를 cancel/gather하고 WS를 닫고 identity를 비운다.

`PlayChannel.check_timeout(self)` — pending 응답 시간이 넘으면 pending을 버리고 WS를 닫아 resync한다.

`PlayChannel.send_command(self, request)`

```text
worker loop에서 0.2초 전송 간격 대기
ready·WS·pending·epoch 확인
command JSON 전송 후 command_id 기록
실패 시 disconnect status; 자동 재전송 안 함
```

`PlayChannel.run(self)`

```text
같은 ClientSession으로 ws(s) /ws/play/, Origin=base_url 연결
첫 mine state까지 timeout 적용
state/snapshot/error를 contracts로 검증해 queue emit
mine matching command_id만 wire pending 종료
끊김 시 pending 폐기, 2초 간격 최대 3회 재연결
```

직접 호출: aiohttp websocket, `read_state/read_snapshot/read_command_id`, `asyncio.wait_for/sleep/gather`, `json.loads`.
