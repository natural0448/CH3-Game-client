"""Account-scoped ClientSession, cookies and CSRF lifecycle."""
from urllib.parse import urlsplit, urlunsplit
from ipaddress import ip_address

import aiohttp

from client.contracts.auth import Identity, read_csrf, read_login
from client.contracts.game import read_state
from client.contracts.ads import EVENT_TYPES, read_ad_event
from client.network.http import JsonHttpClient, ProtocolError


class AdEventRejected(ProtocolError):
    """A refused event requires a fresh selection or a new game login."""
    event_rejected = True


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
        try:
            local_ip = ip_address(urlsplit(self.base_url).hostname).is_loopback
        except ValueError:
            local_ip = False
        self.session = aiohttp.ClientSession(
            cookie_jar=aiohttp.CookieJar(unsafe=local_ip),
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

    async def post_ad_event(self, decision_id: str, event_type: str) -> dict:
        # 23일차 ApiClient: 현재 구조의 AuthSession/JsonHttpClient를 재사용한다.
        if (not isinstance(decision_id, str) or not decision_id
                or len(decision_id) > 128
                or not isinstance(event_type, str) or event_type not in EVENT_TYPES):
            raise ValueError("invalid_ad_event")
        try:
            await self.refresh_csrf()
            data = await self.request_json(
                "POST", "/api/ads/events/",
                payload={"decision_id": decision_id, "event_type": event_type}, csrf=True,
            )
        except ProtocolError as error:
            if error.status in (302, 401):
                raise AdEventRejected("광고 실적을 저장하려면 게임에 다시 로그인하세요.",
                                      error.status) from error
            if error.status in (400, 403, 404):
                reason = {400: str(error), 403: "게임 CSRF 인증이 거절되었습니다.",
                          404: "게임 서버의 광고 사건 경로가 없습니다."}[error.status]
                raise AdEventRejected(f"{reason} 광고 새 요청 필요 (HTTP {error.status}).",
                                      error.status, error.error_code) from error
            raise
        return read_ad_event(data, decision_id, event_type)
