"""Bounded JSON HTTP on the worker-owned session. No UI or logging."""
import json
import aiohttp


class ProtocolError(Exception):
    """Only fixed, credential-free messages may leave the worker."""

    def __init__(self, message, status=None):
        super().__init__(message)
        self.status = status


async def request_json(session, base, http_timeout, method, path, *, payload=None, csrf=False, csrf_token=None):
    if session is None:
        raise ProtocolError("먼저 로그인해 주세요.")
    headers = {"Accept": "application/json"}
    if csrf:
        headers.update({"X-CSRFToken": csrf_token, "Origin": base})
    async with session.request(
        method, base + path, json=payload, headers=headers,
        allow_redirects=False,
        timeout=aiohttp.ClientTimeout(total=http_timeout),
    ) as response:
        status = response.status
        if status != 200:
            if status == 404 and path.startswith("/api/auth/"):
                raise ProtocolError(f"서버에 {path} JSON API가 없어요. 서버는 변경하지 않았습니다.")
            if status in (301, 302, 303, 307, 308):
                raise ProtocolError("다시 로그인해 주세요. 로그인 페이지로 이동하는 응답을 받았어요.", status)
            if status in (401, 403):
                raise ProtocolError("다시 로그인해 주세요. 로그인 정보 또는 세션·CSRF 인증을 확인해 주세요.", status)
            raise ProtocolError(f"API 응답 오류 (HTTP {status}).", status)
        if response.content_type != "application/json":
            raise ProtocolError("JSON API가 HTML 등 다른 형식으로 응답했어요.", status)
        raw = bytearray()
        async for chunk in response.content.iter_chunked(8192):
            raw.extend(chunk)
            if len(raw) > 65536:
                raise ProtocolError("API 응답 크기가 제한을 초과했어요.")
        try:
            data = json.loads(raw)
        except (ValueError, UnicodeError):
            raise ProtocolError("API의 JSON 형식이 올바르지 않아요.") from None
        if not isinstance(data, dict):
            raise ProtocolError("API는 JSON 객체를 반환해야 해요.")
        return data

