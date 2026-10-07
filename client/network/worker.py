"""One thread and one asyncio loop coordinating network components."""
import asyncio
import queue
import threading

import aiohttp

from client.contracts.queries import QUERY_SPECS
from client.network.http import ProtocolError
from client.network.play import PlayChannel
from client.network.queries import QueryGateway
from client.network.session import AuthSession
from client.network.ads import AdGateway


class NetworkWorker:
    QUERY_KINDS = frozenset(QUERY_SPECS)

    def __init__(self, config):
        self.auth = AuthSession(config)
        self.command_timeout = float(config.get("command_timeout_seconds", 8))
        if not 0 < self.command_timeout <= 30:
            raise ValueError("command timeout must be between 0 and 30 seconds")
        self.requests = queue.Queue(maxsize=8)
        self.events = queue.Queue()
        self.thread = threading.Thread(target=self._thread_main, name="village-network")
        self._stop = threading.Event()
        self.loop = None
        self.main_task = None
        self.play = None
        self.queries = None
        self.ads = None
        self._started = False

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

    def drain_events(self, limit=200):
        result = []
        for _ in range(max(0, limit)):
            try:
                result.append(self.events.get_nowait())
            except queue.Empty:
                break
        return result

    def is_alive(self):
        return self.thread.is_alive()

    def stop(self, timeout=None):
        self._stop.set()
        if self.loop is not None and self.main_task is not None and not self.loop.is_closed():
            try:
                self.loop.call_soon_threadsafe(self.main_task.cancel)
            except RuntimeError:
                pass
        if timeout is not None and self._started:
            self.thread.join(timeout=timeout)

    def _emit(self, kind, **data):
        self.events.put({"kind": kind, **data})

    def _thread_main(self):
        try:
            asyncio.run(self._run())
        except asyncio.CancelledError:
            pass
        except Exception:
            self._emit("notice", message="네트워크 작업이 종료됐어요. 접속기를 다시 열어 주세요.")
        finally:
            self._emit("stopped")

    async def _run(self):
        self.loop = asyncio.get_running_loop()
        self.main_task = asyncio.current_task()
        self.play = PlayChannel(self.auth, self._emit, self.command_timeout)
        self.queries = QueryGateway(self.auth, self._emit)
        self.ads = AdGateway(self.auth, self._emit)
        try:
            while not self._stop.is_set():
                await self.play.check_timeout()
                try:
                    request = self.requests.get_nowait()
                except queue.Empty:
                    await asyncio.sleep(0.01)
                    continue
                try:
                    kind = request.get("kind")
                    if kind == "login":
                        await self._login(request)
                    elif kind == "logout":
                        await self._logout()
                    elif kind == "command":
                        await self.play.send_command(request)
                    elif kind in self.QUERY_KINDS:
                        self.queries.start(request)
                    elif kind == "ad":
                        if not self.ads.start(request):
                            self._emit("ad", slot_id=request.get("slot_id"),
                                       request_id=request.get("request_id"), player_id=request.get("player_id"),
                                       status=None, message="광고 요청을 처리 중입니다.")
                    else:
                        self._emit("notice", message="지원하지 않는 네트워크 요청이에요.")
                except (ProtocolError, aiohttp.ClientError, asyncio.TimeoutError, ValueError):
                    self._emit("notice", message="요청을 완료하지 못했어요. 연결과 API 상태를 확인하세요.")
                finally:
                    request.clear()
        finally:
            await self.ads.close()
            await self.queries.close()
            await self.play.close()
            await self.auth.close()
            while True:
                try:
                    self.requests.get_nowait().clear()
                except queue.Empty:
                    break

    async def _login(self, request):
        await self.ads.close()
        await self.queries.close()
        await self.play.close()
        await self.auth.close()
        self._emit("status", phase="authenticating", message="로그인 확인 중…", epoch=self.play.epoch)
        username = request.pop("username", "")
        password = request.pop("password", "")
        try:
            identity = await self.auth.login(username, password)
            self.queries.set_identity(identity)
            self.ads.set_identity(identity)
            self._emit("identity", data=identity.state)
            self.play.start(identity)
        except ProtocolError as exc:
            await self.auth.close()
            self._emit("login_failed", message=str(exc))
        except (aiohttp.ClientError, asyncio.TimeoutError, ValueError):
            await self.auth.close()
            self._emit("login_failed", message="서버에 연결하지 못했어요. 서버 실행과 주소를 확인하세요.")
        finally:
            username = password = ""

    async def _logout(self):
        self._emit("status", phase="logging_out", message="연결을 닫고 로그아웃하는 중…", epoch=self.play.epoch)
        self.queries.invalidate()
        await self.ads.close()
        await self.play.close()
        message = "로그아웃했어요."
        try:
            await self.auth.logout()
        except (ProtocolError, aiohttp.ClientError, asyncio.TimeoutError, ValueError):
            message = "서버 로그아웃을 확인하지 못했어요. 이 접속기의 계정 정보는 지웠습니다."
        finally:
            await self.queries.close()
            await self.auth.close()
            self._emit("logged_out", message=message)
