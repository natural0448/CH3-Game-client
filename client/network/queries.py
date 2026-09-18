"""Button-triggered read-only APIs on the authenticated worker session."""
import asyncio
import time

import aiohttp

from client.contracts.queries import QUERY_SPECS
from client.network.http import ProtocolError


class QueryGateway:
    def __init__(self, auth_session, emit):
        self.auth_session = auth_session
        self.emit = emit
        self.identity = None
        self.tasks = {}
        self.generation = 0
        self.last_requested_at = {kind: float("-inf") for kind in QUERY_SPECS}

    def set_identity(self, identity):
        self.identity = identity
        self.generation += 1

    def invalidate(self):
        self.identity = None
        self.generation += 1

    def start(self, request):
        kind = request.get("kind")
        if kind not in QUERY_SPECS:
            return False
        task = self.tasks.get(kind)
        if task is not None and not task.done():
            return False
        self.tasks[kind] = asyncio.create_task(self.fetch(dict(request)))
        return True

    async def fetch(self, request):
        kind = request["kind"]
        spec = QUERY_SPECS[kind]
        identity = self.identity
        generation = self.generation
        result = {
            "player_id": identity.player_id if identity else None,
            "request_id": request.get("request_id"),
            "path": "GET " + spec.path,
            "status": None,
            "json": None,
        }
        try:
            if identity is None or request.get("player_id") != identity.player_id:
                raise ProtocolError("먼저 로그인해 주세요.")
            now = time.monotonic()
            if now - self.last_requested_at[kind] < spec.minimum_interval:
                raise ProtocolError("전달 상태 조회는 5초 간격으로 할 수 있어요.")
            self.last_requested_at[kind] = now
            data = await self.auth_session.request_json("GET", spec.path)
            result["status"] = 200
            if kind == "history":
                result["json"] = spec.parser(data, identity.player_id)
                present = bool(result["json"].get("events"))
            else:
                result["json"] = spec.parser(data)
                present = True if kind == "delivery" else result["json"].get("available")
            result["message"] = "마지막 조회 결과 · 버튼으로만 갱신" if present else spec.empty_message
        except ProtocolError as exc:
            result["status"] = exc.status if exc.status is not None else result["status"]
            result["message"] = str(exc)
        except (ValueError, TypeError, KeyError, AttributeError, OverflowError):
            result["message"] = "조회 응답의 필드와 형식을 확인해 주세요."
        except (aiohttp.ClientError, asyncio.TimeoutError):
            result["message"] = "조회하지 못했어요. 서버 연결을 확인하고 다시 눌러 주세요."
        if generation == self.generation:
            self.emit(kind, **result)

    async def close(self):
        self.invalidate()
        tasks = [task for task in self.tasks.values() if not task.done()]
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        self.tasks.clear()
        self.last_requested_at = {kind: float("-inf") for kind in QUERY_SPECS}
