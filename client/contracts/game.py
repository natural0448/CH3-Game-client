"""Game wire validation with no UI or network side effects."""

WIDTH, HEIGHT, TILE = 20, 15, 32
GATHER_TILE = (2, 2)
TRAIN_TILE = (3, 2)
STATE_FIELDS = ("player_id", "room_id", "x", "y", "coins", "version")
ERROR_MESSAGES = {
    "outside_map": "마을 경계 밖으로 이동할 수 없어요.",
    "not_at_gather_tile": "채집 장소 (2, 2)로 이동해 주세요.",
    "not_at_train_tile": "개인 수련 장소 (3, 2)로 이동해 주세요.",
    "too_fast": "조금만 기다린 뒤 다시 행동해 주세요.",
    "invalid_direction": "이동 방향을 확인해 주세요.",
    "unknown_action": "지원하지 않는 행동이에요.",
    "object_required": "명령 형식을 확인해 주세요.",
}


def read_state(data):
    if not isinstance(data, dict) or data.get("type") != "state":
        raise ValueError("invalid_state")
    result = {key: data.get(key) for key in STATE_FIELDS}
    for key in ("player_id", "x", "y", "coins", "version"):
        if type(result[key]) is not int:
            raise ValueError("invalid_state")
    if (result["player_id"] <= 0 or not 0 <= result["x"] < WIDTH
            or not 0 <= result["y"] < HEIGHT or result["coins"] < 0
            or result["version"] < 0 or not isinstance(result["room_id"], str)
            or not 1 <= len(result["room_id"]) <= 32):
        raise ValueError("invalid_state")
    username = data.get("username", "")
    result["username"] = username if isinstance(username, str) and len(username) <= 150 else ""
    return result


def read_snapshot(data):
    if not isinstance(data, dict):
        raise ValueError("invalid_snapshot")
    players = data.get("players")
    if not isinstance(players, list) or len(players) > 20:
        raise ValueError("invalid_snapshot")
    return {player["player_id"]: player for player in map(read_state, players)}


def read_command_id(data):
    value = data.get("command_id") if isinstance(data, dict) else None
    return value if isinstance(value, str) and 1 <= len(value) <= 64 else None
