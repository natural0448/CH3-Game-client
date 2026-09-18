"""Authentication response contracts."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Identity:
    player_id: int
    room_id: str
    version: int
    state: dict


def read_csrf(data):
    token = data.get("csrfToken", data.get("csrf_token")) if isinstance(data, dict) else None
    if not isinstance(token, str) or not token or len(token) > 256:
        raise ValueError("invalid_csrf")
    return token


def read_login(data):
    if not isinstance(data, dict) or data.get("authenticated") is not True:
        raise ValueError("invalid_login")
