"""Bounded JSON HTTP policy for the worker-owned session."""
import json

import aiohttp


class ProtocolError(Exception):
    def __init__(self, message, status=None, error_code=None):
        super().__init__(message)
        self.status = status
        self.error_code = error_code


class JsonHttpClient:
    def __init__(self, session, base_url, timeout, origin):
        self.session = session
        self.base_url = base_url
        self.timeout = timeout
        self.origin = origin

    async def request_json(self, method, path, *, payload=None, csrf_token=None):
        if self.session is None or self.session.closed:
            raise ProtocolError("먼저 로그인해 주세요.")
        headers = {"Accept": "application/json"}
        if csrf_token is not None:
            headers.update({"X-CSRFToken": csrf_token, "Origin": self.origin})
        response_timeout = aiohttp.ClientTimeout(total=self.timeout)
        async with self.session.request(
            method, self.base_url + path, json=payload, headers=headers,
            allow_redirects=False, timeout=response_timeout,
        ) as response:
            if path == "/api/ads/events/" and response.status == 400:
                known = {
                    "decision_snapshot_missing": "기존 결정에 저장된 정보가 부족합니다.",
                    "decision_not_found_for_subject": "현재 수신자의 광고 결정이 아닙니다.",
                    "impression_required": "서버에서 선행 노출을 확인하지 못했습니다.",
                }
                code = None
                if response.content_type == "application/json":
                    try:
                        raw = await response.content.read(65536)
                        data = json.loads(raw)
                        candidate = data.get("error") if isinstance(data, dict) else None
                        if isinstance(candidate, str) and candidate in known:
                            code = candidate
                    except (ValueError, UnicodeError):
                        pass
                raise ProtocolError(known.get(code, "광고 사건이 거절되었습니다."), 400, code)
            if response.status in (301, 302, 303, 307, 308, 401, 403):
                raise ProtocolError("로그인이 필요하거나 인증이 만료됐어요.", response.status)
            if response.status < 200 or response.status >= 300:
                raise ProtocolError("서버가 요청을 처리하지 못했어요.", response.status)
            if response.content_type != "application/json":
                raise ProtocolError("서버가 JSON 대신 다른 형식을 보냈어요.", response.status)
            chunks = []
            size = 0
            async for chunk in response.content.iter_chunked(8192):
                size += len(chunk)
                if size > 65536:
                    raise ProtocolError("서버 JSON 응답이 너무 커요.", response.status)
                chunks.append(chunk)
            try:
                data = json.loads(b"".join(chunks))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise ProtocolError("서버 JSON을 읽지 못했어요.", response.status) from exc
            if not isinstance(data, dict):
                raise ProtocolError("서버 JSON은 객체여야 해요.", response.status)
            return data
