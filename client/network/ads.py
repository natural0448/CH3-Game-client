"""Nonblocking ad selection and bounded PNG bytes on the existing game session."""
import asyncio
import struct
import time

import aiohttp

from client.contracts.ads import CREATIVE_PATHS, SLOTS, read_decision
from client.network.http import ProtocolError


class AdGateway:
    def __init__(self, auth_session, emit):
        self.auth = auth_session
        self.emit = emit
        self.identity = None
        self.generation = 0
        self.tasks = {}
        self.last_requested = {}

    def set_identity(self, identity):
        self.identity = identity
        self.generation += 1

    def start(self, request):
        slot = request.get("slot_id")
        if not isinstance(slot, str) or slot not in SLOTS or (slot in self.tasks and not self.tasks[slot].done()):
            return False
        self.tasks[slot] = asyncio.create_task(self.fetch(dict(request)))
        return True

    async def fetch(self, request):
        generation, identity = self.generation, self.identity
        slot = request["slot_id"]
        result = {"slot_id": slot, "request_id": request.get("request_id"),
                  "player_id": identity.player_id if identity else None,
                  "decision": None, "image_bytes": None, "status": None}
        try:
            if identity is None or request.get("player_id") != identity.player_id:
                raise ProtocolError("게임 로그인이 필요합니다.")
            now = time.monotonic()
            if now - self.last_requested.get(slot, float("-inf")) < 15:
                raise ProtocolError("새 광고는 15초 간격으로 요청해 주세요.")
            self.last_requested[slot] = now
            data = await self.auth.request_json("POST", "/api/ads/decision/",
                                                payload={"slot_id": slot}, csrf=True)
            decision = read_decision(data, slot)
            if decision and decision["creative_path"]:
                result["image_bytes"] = await self.fetch_png(decision["creative_path"])
            result.update(decision=decision, status=200,
                          message="광고 표시 준비 완료" if decision else "선택할 광고가 없습니다.")
        except ProtocolError as exc:
            result.update(message=str(exc), status=exc.status)
        except (aiohttp.ClientError, asyncio.TimeoutError, ValueError, KeyError, TypeError, struct.error):
            result["message"] = "광고 또는 이미지를 읽을 수 없습니다. 서버 연결을 확인하세요."
        if generation == self.generation:
            self.emit("ad", **result)

    async def fetch_png(self, path):
        if not isinstance(path, str) or not path or path not in CREATIVE_PATHS:
            raise ValueError("invalid_png_path")
        async with self.auth.session.get(self.auth.base_url + path, allow_redirects=False,
                                         timeout=aiohttp.ClientTimeout(total=3)) as response:
            if response.status != 200 or response.content_type != "image/png":
                raise ValueError("invalid_png_response")
            chunks, size = [], 0
            async for chunk in response.content.iter_chunked(8192):
                size += len(chunk)
                if size > 1048576:
                    raise ValueError("oversized_png")
                chunks.append(chunk)
            raw = b"".join(chunks)
            if len(raw) < 24 or raw[:8] != b"\x89PNG\r\n\x1a\n":
                raise ValueError("invalid_png")
            width, height = struct.unpack(">II", raw[16:24])
            if not 1 <= width <= 1024 or not 1 <= height <= 1024:
                raise ValueError("oversized_png_dimensions")
            return raw

    async def close(self):
        self.generation += 1
        self.identity = None
        tasks = [task for task in self.tasks.values() if not task.done()]
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        self.tasks.clear()
        self.last_requested.clear()
