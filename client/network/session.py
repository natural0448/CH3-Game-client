"""Account-scoped ClientSession, cookies and CSRF lifecycle."""
from urllib.parse import urlsplit, urlunsplit

import aiohttp

from client.contracts.auth import Identity, read_csrf, read_login
from client.contracts.game import read_state
from client.network.http import JsonHttpClient, ProtocolError


def server_urls(base):
    parts = urlsplit(base)
    if (parts.scheme not in ("http", "https") or not parts.hostname
            or parts.username or parts.password or parts.path not in ("", "/")
            or parts.query or parts.fragment):
        raise ValueError("server_base_url must be an http(s) origin without a path or credentials")
    origin = urlunsplit((parts.scheme, parts.netloc, "", "", ""))
    websocket = urlunsplit(("wss" if parts.scheme == "https" else "ws",
                            parts.netloc, "/ws/play/", "", ""))
    return origin, websocket


class AuthSession:
    def __init__(self, config):
        self.base_url, self.ws_url = server_urls(config["server_base_url"])
        self.timeout = float(config.get("http_timeout_seconds", 8))
        if not 0 < self.timeout <= 30:
            raise ValueError("http timeout must be between 0 and 30 seconds")
        self.session = None
        self.http = None
        self.csrf = None

    async def open(self):
        await self.close()
        self.session = aiohttp.ClientSession(
            cookie_jar=aiohttp.CookieJar(unsafe=True),
            timeout=aiohttp.ClientTimeout(total=self.timeout),
        )
        self.http = JsonHttpClient(self.session, self.base_url, self.timeout, self.base_url)

    async def close(self):
        if self.session is not None:
            self.session.cookie_jar.clear()
            await self.session.close()
        self.session = None
        self.http = None
        self.csrf = None

    async def request_json(self, method, path, *, payload=None, csrf=False):
        if self.http is None:
            raise ProtocolError("먼저 로그인해 주세요.")
        return await self.http.request_json(
            method, path, payload=payload,
            csrf_token=self.csrf if csrf else None,
        )

    async def refresh_csrf(self):
        try:
            self.csrf = read_csrf(await self.request_json("GET", "/api/auth/csrf/"))
        except ValueError as exc:
            raise ProtocolError("CSRF API에 csrfToken 문자열이 필요해요.") from exc

    async def login(self, username, password):
        await self.open()
        await self.refresh_csrf()
        try:
            read_login(await self.request_json(
                "POST", "/api/auth/login/",
                payload={"username": username, "password": password}, csrf=True,
            ))
        except ValueError as exc:
            raise ProtocolError("서버가 로그인 성공을 확인하지 않았어요.") from exc
        await self.refresh_csrf()
        state = read_state(await self.request_json("GET", "/api/player/"))
        return Identity(state["player_id"], state["room_id"], state["version"], {"type": "state", **state})

    async def logout(self):
        if self.session is None:
            return
        await self.refresh_csrf()
        result = await self.request_json("POST", "/api/auth/logout/", payload={}, csrf=True)
        if result.get("authenticated") is not False:
            raise ProtocolError("서버 로그아웃 확인이 필요해요.")
