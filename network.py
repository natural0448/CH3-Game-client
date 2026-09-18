"""One worker thread, one asyncio loop, private in-memory HTTP/WS session.

Required server contract (not added/changed by this client):
GET /api/auth/csrf/ -> {"csrfToken": "..."} (csrf_token also accepted)
POST /api/auth/login/ <- {"username": "...", "password": "..."} -> JSON 200
GET /api/auth/csrf/ again after login's CSRF rotation
GET /api/player/ -> state JSON, then WS /ws/play/ -> state/error
POST /api/auth/logout/ with the latest CSRF header + Origin -> JSON 200.
No HTML form fallback, disk cookie jar, credential logging, or automatic replay.
"""

import asyncio
import json
import queue
import threading
import time
from urllib.parse import urlsplit, urlunsplit

import aiohttp

from state import ERROR_MESSAGES, read_snapshot, read_state
from history_data import read_history
from analytics_data import API_RESPONSE_FIELDS, read_analytics, read_actions
from http_client import ProtocolError, request_json


def server_urls(base):
    parts = urlsplit(base)
    if (parts.scheme not in ("http", "https") or not parts.hostname
            or parts.username or parts.password or parts.path not in ("", "/")
            or parts.query or parts.fragment):
        raise ValueError("server_base_url must be an http(s) origin without a path or credentials")
    base = urlunsplit((parts.scheme, parts.netloc, "", "", ""))
    websocket = urlunsplit(("wss" if parts.scheme == "https" else "ws",
                            parts.netloc, "/ws/play/", "", ""))
    return base, websocket


class NetworkWorker:
    def __init__(self, config):
        self.base, self.ws_url = server_urls(config["server_base_url"])
        self.http_timeout = float(config.get("http_timeout_seconds", 8))
        self.command_timeout = float(config.get("command_timeout_seconds", 8))
        if not 0 < self.http_timeout <= 30 or not 0 < self.command_timeout <= 30:
            raise ValueError("timeouts must be between 0 and 30 seconds")
        self.requests = queue.Queue(maxsize=8)
        self.events = queue.Queue()
        self.thread = threading.Thread(target=self._thread_main, name="village-network")
        self._stop = threading.Event()
        self.loop = self.main_task = self.ws_task = self.session = self.ws = None
        self.identity = None
        self.room_id = None
        self.version = -1
        self.csrf = None
        self.ready = False
        self.pending = None
        self.sent_at = float("-inf")
        self.epoch = 0
        self._started = False
        self.delivery_task = None
        self.analytics_task = None
        self.history_task = None
        self.actions_task = None
        self.delivery_sent_at = float("-inf")

    def start(self):
        if self._started:
            raise RuntimeError("The network worker can only be started once")
        self._started = True
        self.thread.start()

    def submit(self, request):
        if self._stop.is_set():
            return False
        try:
            self.requests.put_nowait(dict(request))
            return True
        except queue.Full:
            return False

    def stop(self):
        self._stop.set()
        if self.loop and self.main_task and not self.loop.is_closed():
            try:
                self.loop.call_soon_threadsafe(self.main_task.cancel)
            except RuntimeError:
                pass  # Worker already completed cleanup.

    def _emit(self, kind, **data):
        self.events.put({"kind": kind, **data})

    def _status(self, phase, message):
        self._emit("status", phase=phase, message=message, epoch=self.epoch)

    def _thread_main(self):
        try:
            asyncio.run(self._run())
        except asyncio.CancelledError:
            pass
        except Exception:
            # Never emit exception repr: HTTP exceptions can contain auth headers.
            self._emit("notice", message="네트워크 작업이 종료됐어요. 접속기를 다시 열어 주세요.")
        finally:
            self._emit("stopped")

    async def _run(self):
        self.loop = asyncio.get_running_loop()
        self.main_task = asyncio.current_task()
        try:
            while not self._stop.is_set():
                try:
                    request = self.requests.get_nowait()
                except queue.Empty:
                    if self.pending and time.monotonic() - self.sent_at > self.command_timeout:
                        self.ready = False
                        self._status("disconnected", "응답 시간이 초과됐어요. 서버 상태를 다시 확인합니다.")
                        if self.ws:
                            await self.ws.close()
                        self.pending = None
                    await asyncio.sleep(0.01)
                    continue
                try:
                    kind = request.get("kind")
                    if kind == "login":
                        await self._login(request)
                    elif kind == "logout":
                        await self._logout()
                    elif kind == "command":
                        await self._command(request)
                    elif kind == "delivery":
                        if self.delivery_task is None or self.delivery_task.done():
                            self.delivery_task = asyncio.create_task(self._delivery())
                    elif kind in ("analytics", "history", "actions"):
                        task_name = kind + "_task"
                        task = getattr(self, task_name)
                        if task is None or task.done():
                            handler = getattr(self, "_" + kind)
                            setattr(self, task_name, asyncio.create_task(handler(dict(request))))
                except (ProtocolError, aiohttp.ClientError, asyncio.TimeoutError, ValueError):
                    self._emit("notice", message="요청을 완료하지 못했어요. 연결과 API 상태를 확인하세요.")
                finally:
                    request.clear()  # Remove login password references promptly.
        finally:
            await self._close_ws()
            await self._close_session()
            while True:
                try:
                    self.requests.get_nowait().clear()
                except queue.Empty:
                    break

    async def _close_ws(self):
        self.ready = False
        self.pending = None
        if self.ws_task:
            self.ws_task.cancel()
            await asyncio.gather(self.ws_task, return_exceptions=True)
            self.ws_task = None
        if self.ws and not self.ws.closed:
            await self.ws.close()
        self.ws = None

    async def _close_session(self):
        for name in ("history_task", "analytics_task", "actions_task", "delivery_task"):
            task = getattr(self, name)
            if task:
                task.cancel()
                await asyncio.gather(task, return_exceptions=True)
                setattr(self, name, None)
        if self.session:
            self.session.cookie_jar.clear()
            await self.session.close()
        self.session = None
        self.csrf = self.identity = None
        self.room_id = None
        self.version = -1
        self.delivery_sent_at = float("-inf")

    async def _json(self, method, path, *, payload=None, csrf=False):
        return await request_json(self.session, self.base, self.http_timeout, method, path,
                                  payload=payload, csrf=csrf, csrf_token=self.csrf)

    async def _get_csrf(self):
        data = await self._json("GET", "/api/auth/csrf/")
        token = data.get("csrfToken", data.get("csrf_token"))
        if not isinstance(token, str) or not token or len(token) > 256:
            raise ProtocolError("CSRF API에 csrfToken 문자열이 필요해요.")
        self.csrf = token

    async def _delivery(self):
        player_id = self.identity
        result = dict(player_id=player_id, path="GET /api/delivery/", status=None, json=None)
        try:
            if self.session is None or player_id is None:
                raise ProtocolError("먼저 로그인해 주세요.")
            now = time.monotonic()
            if now - self.delivery_sent_at < 5:
                raise ProtocolError("전달 상태 조회는 5초 간격으로 할 수 있어요.")
            self.delivery_sent_at = now
            data = await self._json("GET", "/api/delivery/")
            result["status"] = 200
            counts = (data.get("event_count"), data.get("pending_publish_count"))
            if any(type(value) is not int or value < 0 for value in counts) or data.get("source") != "mysql-outbox":
                raise ProtocolError("이벤트 전달 상태의 응답 형식을 확인해 주세요.")
            result["json"] = {key: data[key] for key in API_RESPONSE_FIELDS["/api/delivery/"]}
            result["message"] = "마지막 조회 결과 · 자동 갱신 없음"
        except ProtocolError as exc:
            result["status"] = exc.status if exc.status is not None else result["status"]
            result["message"] = str(exc)
        except (aiohttp.ClientError, asyncio.TimeoutError, ValueError):
            result["message"] = "조회에 실패했어요. 서버 연결을 확인하고 다시 눌러 주세요."
        self._emit("delivery", **result)

    async def _player(self):
        data = await self._json("GET", "/api/player/")
        state = read_state(data)
        if self.identity is not None and state["player_id"] != self.identity:
            raise ProtocolError("로그인 계정과 응답의 플레이어가 일치하지 않아요.")
        safe = {"type": "state", **state}
        return safe

    async def _read_panel(self, request, *, kind, path, parser, empty_message):
        """Read-only query interface: worker JSON in, correlated safe event out."""
        identity = self.identity
        result = dict(player_id=identity, request_id=request.get("request_id"),
                      path="GET " + path, status=None, json=None)
        try:
            if self.session is None or identity is None or request.get("player_id") != identity:
                raise ProtocolError("먼저 로그인해 주세요.")
            data = await self._json("GET", path)
            result["status"] = 200
            result["json"] = parser(data)
            safe = result["json"]
            present = bool(safe.get("events")) if kind == "history" else safe.get("available")
            result["message"] = "마지막 조회 결과 · 버튼으로만 갱신" if present else empty_message
        except ProtocolError as exc:
            result["status"] = exc.status if exc.status is not None else result["status"]
            result["message"] = str(exc)
        except (ValueError, TypeError, KeyError, AttributeError, OverflowError):
            result["message"] = "조회 응답의 필드와 형식을 확인해 주세요."
        except (aiohttp.ClientError, asyncio.TimeoutError):
            result["message"] = "조회하지 못했어요. 서버 연결을 확인하고 다시 눌러 주세요."
        self._emit(kind, **result)

    async def _analytics(self, request):
        await self._read_panel(request, kind="analytics", path="/api/analytics/",
                               parser=read_analytics, empty_message="아직 첫 집계가 없습니다")

    async def _actions(self, request):
        await self._read_panel(request, kind="actions", path="/api/analytics/actions/",
                               parser=read_actions, empty_message="행동 집계가 아직 없습니다")

    async def _history(self, request):
        identity = self.identity
        await self._read_panel(request, kind="history", path="/api/history/",
                               parser=lambda data: read_history(data, identity),
                               empty_message="아직 행동 기록이 없습니다")

    async def _login(self, request):
        await self._close_ws()
        await self._close_session()
        self._status("authenticating", "로그인 확인 중…")
        # Each client instance owns a separate jar; unsafe permits local IP cookies.
        self.session = aiohttp.ClientSession(
            cookie_jar=aiohttp.CookieJar(unsafe=True),
            timeout=aiohttp.ClientTimeout(total=self.http_timeout),
        )
        try:
            await self._get_csrf()
            result = await self._json("POST", "/api/auth/login/", payload={
                "username": request.pop("username", ""),
                "password": request.pop("password", ""),
            }, csrf=True)
            if result.get("authenticated") is not True:
                raise ProtocolError("서버가 로그인 성공을 확인하지 않았어요.")
            await self._get_csrf()
            data = await self._player()
            self.identity = data["player_id"]
            self.room_id = data["room_id"]
            self.version = data["version"]
            self._emit("identity", data=data)
            self.ws_task = asyncio.create_task(self._websockets())
        except ProtocolError as exc:
            await self._close_session()
            self._emit("login_failed", message=str(exc))
        except (aiohttp.ClientError, asyncio.TimeoutError, ValueError):
            await self._close_session()
            self._emit("login_failed", message="서버에 연결하지 못했어요. 서버 실행과 주소를 확인하세요.")

    async def _logout(self):
        self._status("logging_out", "연결을 닫고 로그아웃하는 중…")
        await self._close_ws()
        message = "로그아웃했어요."
        try:
            if self.session:
                await self._get_csrf()
                result = await self._json("POST", "/api/auth/logout/", payload={}, csrf=True)
                if result.get("authenticated") is not False:
                    raise ProtocolError("서버 로그아웃 확인이 필요해요.")
        except (ProtocolError, aiohttp.ClientError, asyncio.TimeoutError, ValueError):
            message = "서버 로그아웃을 확인하지 못했어요. 이 접속기의 계정 정보는 지웠습니다."
        finally:
            await self._close_session()
            self._emit("logged_out", message=message)

    async def _command(self, request):
        command = request["command"]
        # The UI and socket clocks differ slightly; wait in the worker, never the UI.
        delay = 0.2 - (time.monotonic() - self.sent_at)
        if delay > 0:
            await asyncio.sleep(delay)
        if (not self.ready or not self.ws or self.ws.closed or self.pending
                or request.get("epoch") != self.epoch):
            # No fabricated server acknowledgement. Drop the connection to resync.
            self.ready = False
            self._status("disconnected", "전송할 수 없는 상태예요. 서버 상태를 다시 확인합니다.")
            if self.ws:
                await self.ws.close()
            return
        self.pending = command["command_id"]
        self.sent_at = time.monotonic()
        try:
            await self.ws.send_json(command)
        except (aiohttp.ClientError, ConnectionError, RuntimeError):
            self.ready = False
            self._status("disconnected", "연결이 끊겼어요. 전송 중 행동은 다시 보내지 않습니다.")
            await self.ws.close()

    async def _websockets(self):
        retries = 0
        while True:
            if retries:
                self._status("reconnecting", f"연결 끊김 · 2초 뒤 재연결 {retries}/3")
                await asyncio.sleep(2)
            self.epoch += 1
            self._status("connecting", "서버의 첫 상태를 기다리는 중…")
            first = True
            try:
                self.ws = await self.session.ws_connect(
                    self.ws_url, origin=self.base, heartbeat=5,
                    timeout=aiohttp.ClientWSTimeout(ws_close=2),
                    max_msg_size=65536,
                )
                while True:
                    if first:
                        message = await asyncio.wait_for(self.ws.receive(), self.http_timeout)
                    else:
                        message = await self.ws.receive()
                    if message.type != aiohttp.WSMsgType.TEXT:
                        break
                    data = json.loads(message.data)
                    if not isinstance(data, dict):
                        raise ValueError("invalid_message")
                    if data.get("type") == "state":
                        state = read_state(data)
                        if state["room_id"] != self.room_id:
                            continue
                        mine = state["player_id"] == self.identity
                        if mine and state["version"] < self.version:
                            continue
                        if mine:
                            self.version = state["version"]
                        safe = {"type": "state", **state}
                        command_id = data.get("command_id")
                        if isinstance(command_id, str) and len(command_id) <= 64:
                            safe["command_id"] = command_id
                        if mine and command_id and command_id == self.pending:
                            self.pending = None
                        self._emit("state", data=safe, epoch=self.epoch, first=first and mine)
                        if mine:
                            self.ready = True
                            first = False
                            retries = 0
                    elif data.get("type") == "snapshot":
                        members = read_snapshot(data)
                        safe = {"type": "snapshot", "players": [
                            {"type": "state", **player} for player in members.values()
                            if player["room_id"] == self.room_id
                        ]}
                        self._emit("snapshot", data=safe, epoch=self.epoch)
                    elif data.get("type") == "error":
                        command_id = data.get("command_id")
                        if command_id and command_id == self.pending:
                            self.pending = None
                        code = data.get("code")
                        self._emit("error", epoch=self.epoch,
                                   code=code if isinstance(code, str) and code in ERROR_MESSAGES else "rejected",
                                   command_id=command_id if isinstance(command_id, str) and len(command_id) <= 64 else None)
            except (aiohttp.ClientError, asyncio.TimeoutError, ValueError, ConnectionError):
                pass
            finally:
                self.ready = False
                self.pending = None
                self._status("disconnected", "연결이 끊겼어요. 조작을 잠시 멈춥니다.")
                if self.ws and not self.ws.closed:
                    await self.ws.close()
                self.ws = None
            if retries >= 3:
                self._status("disconnected", "재연결 3회를 마쳤어요. 로그아웃 후 다시 로그인해 주세요.")
                return
            retries += 1
