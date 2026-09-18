"""행동 이력의 표시 허용 필드만 복사한다. 인증 정보는 결과 큐에 넣지 않는다."""
from datetime import datetime
from uuid import UUID


def read_history(data, player_id):
    if data.get("scope") != "current-player" or type(data.get("limit")) is not int or data["limit"] != 20:
        raise ValueError("invalid_history")
    events = data.get("events")
    if not isinstance(events, list) or len(events) > 20:
        raise ValueError("invalid_history")
    safe = []
    for event in events:
        if not isinstance(event, dict) or event.get("player_id") != player_id or type(event.get("player_id")) is not int:
            raise ValueError("invalid_history_owner")
        UUID(event["event_id"])
        if type(event.get("schema_version")) is not int or event["schema_version"] != 1:
            raise ValueError("invalid_history_schema")
        for field, limit in (("event_type", 40), ("room_id", 32), ("event_time", 64)):
            if not isinstance(event.get(field), str) or not 1 <= len(event[field]) <= limit or not event[field].isprintable():
                raise ValueError("invalid_history_text")
        if datetime.fromisoformat(event["event_time"]).tzinfo is None:
            raise ValueError("invalid_history_time")
        payload = event["payload"]
        clean = {}
        for key in ("x", "y", "coins", "version"):
            if type(payload.get(key)) is not int:
                raise ValueError("invalid_history_state")
            clean[key] = payload[key]
        if "command_id" in payload:
            clean["command_id"] = str(UUID(payload["command_id"]))
        transition = payload.get("transition")
        if transition is not None:
            item = {"episode_id": str(UUID(transition["episode_id"]))}
            for key in ("step", "reward"):
                if type(transition.get(key)) is not int:
                    raise ValueError("invalid_transition")
                item[key] = transition[key]
            if not 1 <= item["step"] <= 5:
                raise ValueError("invalid_transition_step")
            for key in ("done", "terminated", "truncated"):
                if type(transition.get(key)) is not bool:
                    raise ValueError("invalid_transition_flag")
                item[key] = transition[key]
            if transition.get("policy_version") != "manual-v1":
                raise ValueError("invalid_transition_policy")
            item["policy_version"] = "manual-v1"
            action = transition["action"]
            if action.get("type") not in ("move", "gather", "train"):
                raise ValueError("invalid_transition_action")
            item["action"] = {"type": action["type"]}
            if action["type"] == "move":
                if action.get("direction") not in ("up", "down", "left", "right"):
                    raise ValueError("invalid_transition_direction")
                item["action"]["direction"] = action["direction"]
            for key in ("observation", "next_observation"):
                observation = transition[key]
                if any(type(observation.get(field)) is not int for field in ("x", "y", "coins")):
                    raise ValueError("invalid_observation")
                item[key] = {field: observation[field] for field in ("x", "y", "coins")}
            clean["transition"] = item
        safe.append({**{key: event[key] for key in (
            "schema_version", "event_id", "event_type", "player_id", "room_id", "event_time"
        )}, "payload": clean})
    return {"scope": "current-player", "limit": 20, "events": safe}
