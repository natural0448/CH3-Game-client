"""WebSocket play channel and reconnect policy."""
import asyncio
import json
import time

import aiohttp

from client.contracts.game import ERROR_MESSAGES, read_command_id, read_snapshot, read_state


class PlayChannel:
    def __init__(self, auth_session, emit, command_timeout):
        self.auth_session = auth_session
        self.emit = emit
        self.command_timeout = command_timeout
        self.identity = None
        self.ws = None
        self.task = None
        self.ready = False
        self.pending = None
        self.sent_at = float("-inf")
        self.epoch = 0
        self.version = -1
        self.closing = False

    def status(self, phase, message):
        self.emit("status", phase=phase, message=message, epoch=self.epoch)

    def start(self, identity):
        self.identity = identity
        self.version = identity.version
        self.closing = False
        self.task = asyncio.create_task(self.run())

    async def close(self):
        self.closing = True
        self.ready = False
        self.pending = None
        current = asyncio.current_task()
        if self.task is not None and self.task is not current:
            self.task.cancel()
            await asyncio.gather(self.task, return_exceptions=True)
        self.task = None
        if self.ws is not None and not self.ws.closed:
            await self.ws.close()
        self.ws = None
        self.identity = None

    async def check_timeout(self):
        if self.pending and time.monotonic() - self.sent_at > self.command_timeout:
            self.ready = False
            self.status("disconnected", "응답 시간이 초과됐어요. 서버 상태를 다시 확인합니다.")
            self.pending = None
            if self.ws is not None and not self.ws.closed:
                await self.ws.close()

    async def send_command(self, request):
        command = request.get("command")
        if not isinstance(command, dict):
            return
        delay = 0.2 - (time.monotonic() - self.sent_at)
        if delay > 0:
            await asyncio.sleep(delay)
        if (not self.ready or self.ws is None or self.ws.closed or self.pending
                or request.get("epoch") != self.epoch):
            self.ready = False
            self.status("disconnected", "전송할 수 없는 상태예요. 서버 상태를 다시 확인합니다.")
            if self.ws is not None and not self.ws.closed:
                await self.ws.close()
            return
        self.pending = command.get("command_id")
        self.sent_at = time.monotonic()
        try:
            await self.ws.send_json(command)
        except (aiohttp.ClientError, ConnectionError, RuntimeError):
            self.ready = False
            self.status("disconnected", "연결이 끊겼어요. 전송 중 행동은 다시 보내지 않습니다.")
            if self.ws is not None and not self.ws.closed:
                await self.ws.close()

    async def run(self):
        retries = 0
        try:
            while not self.closing and self.identity is not None:
                if retries:
                    self.status("reconnecting", f"연결 끊김 · 2초 뒤 재연결 {retries}/3")
                    await asyncio.sleep(2)
                self.epoch += 1
                self.status("connecting", "서버의 첫 상태를 기다리는 중…")
                first = True
                try:
                    session = self.auth_session.session
                    if session is None:
                        return
                    self.ws = await session.ws_connect(
                        self.auth_session.ws_url,
                        origin=self.auth_session.base_url,
                        heartbeat=5,
                        timeout=aiohttp.ClientWSTimeout(ws_close=2),
                        max_msg_size=65536,
                    )
                    while not self.closing:
                        message = await (asyncio.wait_for(self.ws.receive(), self.auth_session.timeout)
                                         if first else self.ws.receive())
                        if message.type != aiohttp.WSMsgType.TEXT:
                            break
                        data = json.loads(message.data)
                        if not isinstance(data, dict):
                            raise ValueError("invalid_message")
                        message_type = data.get("type")
                        if message_type == "state":
                            state = read_state(data)
                            if state["room_id"] != self.identity.room_id:
                                continue
                            mine = state["player_id"] == self.identity.player_id
                            if mine and state["version"] < self.version:
                                continue
                            if mine:
                                self.version = state["version"]
                            safe = {"type": "state", **state}
                            command_id = read_command_id(data)
                            if command_id is not None:
                                safe["command_id"] = command_id
                            if mine and command_id == self.pending:
                                self.pending = None
                            self.emit("state", data=safe, epoch=self.epoch, first=first and mine)
                            if mine:
                                self.ready = True
                                first = False
                                retries = 0
                        elif message_type == "snapshot":
                            members = read_snapshot(data)
                            safe = {"type": "snapshot", "players": [
                                {"type": "state", **player} for player in members.values()
                                if player["room_id"] == self.identity.room_id
                            ]}
                            self.emit("snapshot", data=safe, epoch=self.epoch)
                        elif message_type == "error":
                            command_id = read_command_id(data)
                            if command_id == self.pending:
                                self.pending = None
                            code = data.get("code")
                            self.emit("error", epoch=self.epoch,
                                      code=code if isinstance(code, str) and code in ERROR_MESSAGES else "rejected",
                                      command_id=command_id)
                except (aiohttp.ClientError, asyncio.TimeoutError, ValueError, ConnectionError):
                    pass
                finally:
                    self.ready = False
                    self.pending = None
                    if self.ws is not None and not self.ws.closed:
                        await self.ws.close()
                    self.ws = None
                    if not self.closing:
                        self.status("disconnected", "연결이 끊겼어요. 조작을 잠시 멈춥니다.")
                if self.closing:
                    return
                if retries >= 3:
                    self.status("disconnected", "재연결 3회를 마쳤어요. 로그아웃 후 다시 로그인해 주세요.")
                    return
                retries += 1
        except asyncio.CancelledError:
            raise
