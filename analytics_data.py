"""Read-only response contracts. Copy only documented fields into the UI."""
from datetime import datetime


API_RESPONSE_FIELDS = {
    "/api/analytics/actions/": ("available", "source_topic", "source_kind", "raw_record_count", "bounds", "label_source", "summary"),
    "/api/history/": ("scope", "limit", "events"),
    "/api/delivery/": ("event_count", "pending_publish_count", "source"),
    "/api/analytics/": ("available", "schema_version", "generated_at", "event_count", "by_action", "by_room"),
}


def read_analytics(data):
    if type(data.get("available")) is not bool:
        raise ValueError("invalid_analytics")
    if not data["available"]:
        return {"available": False}
    if type(data.get("schema_version")) is not int or data["schema_version"] != 1:
        raise ValueError("invalid_analytics")
    if type(data.get("event_count")) is not int or data["event_count"] < 0:
        raise ValueError("invalid_analytics")
    timestamp = data.get("generated_at")
    if not isinstance(timestamp, str) or len(timestamp) > 64 or datetime.fromisoformat(timestamp).tzinfo is None:
        raise ValueError("invalid_analytics")
    safe = {key: data[key] for key in ("available", "schema_version", "generated_at", "event_count")}
    for field, key in (("by_action", "event_type"), ("by_room", "room_id")):
        rows = data.get(field)
        if not isinstance(rows, list) or len(rows) > 100:
            raise ValueError("invalid_analytics")
        safe[field] = []
        for row in rows:
            if (not isinstance(row, dict) or not isinstance(row.get(key), str)
                    or not 1 <= len(row[key]) <= 128 or not row[key].isprintable()
                    or type(row.get("count")) is not int or row["count"] < 0):
                raise ValueError("invalid_analytics")
            safe[field].append({key: row[key], "count": row["count"]})
    return {key: safe[key] for key in API_RESPONSE_FIELDS["/api/analytics/"]}


ACTION_TYPES = ("player.moved", "player.gathered", "player.trained")


def _count(value):
    if type(value) is not int or value < 0:
        raise ValueError("invalid_action_count")
    return value


def _text(value, limit=128):
    if not isinstance(value, str) or not 1 <= len(value) <= limit or not value.isprintable():
        raise ValueError("invalid_action_text")
    return value


def read_actions(data):
    """Validate snapshot metrics separately from authoritative player state."""
    if not isinstance(data, dict) or type(data.get("available")) is not bool:
        raise ValueError("invalid_actions")
    if not data["available"]:
        return {"available": False, "summary": None}
    if (data.get("source_topic") != "game.actions.v1"
            or data.get("source_kind") != "bounded-kafka-snapshot"):
        raise ValueError("invalid_action_source")
    summary = data.get("summary")
    if not isinstance(summary, dict):
        raise ValueError("invalid_action_summary")
    stamp = _text(summary.get("generated_at"), 64)
    if datetime.fromisoformat(stamp).tzinfo is None:
        raise ValueError("invalid_action_time")
    clean = {"generated_at": stamp, "event_count": _count(summary.get("event_count"))}
    for field, key, limit in (("by_action", "event_type", 3), ("by_room", "room_id", 100)):
        rows = summary.get(field)
        if not isinstance(rows, list) or len(rows) > limit:
            raise ValueError("invalid_action_rows")
        clean[field] = []
        seen = set()
        for row in rows:
            if not isinstance(row, dict):
                raise ValueError("invalid_action_row")
            name = _text(row.get(key))
            if name in seen or (field == "by_action" and name not in ACTION_TYPES):
                raise ValueError("invalid_action_row_key")
            seen.add(name)
            item = {key: name, "count": _count(row.get("count"))}
            if field == "by_action":
                item["action_label"] = _text(row.get("action_label"), 64)
            clean[field].append(item)
    result = {"available": True, "source_topic": data["source_topic"],
              "source_kind": data["source_kind"], "summary": clean,
              "raw_record_count": _count(data.get("raw_record_count"))}
    if "label_source" in data:
        if data["label_source"] != "current-display-map":
            raise ValueError("invalid_label_source")
        result["label_source"] = data["label_source"]
    if "bounds" in data:
        if not isinstance(data["bounds"], list) or len(data["bounds"]) > 100:
            raise ValueError("invalid_bounds")
        result["bounds"] = []
        for row in data["bounds"]:
            if not isinstance(row, dict):
                raise ValueError("invalid_bounds")
            bound = {key: _count(row.get(key)) for key in ("partition", "start_inclusive", "end_exclusive")}
            if bound["start_inclusive"] > bound["end_exclusive"]:
                raise ValueError("invalid_bounds")
            result["bounds"].append(bound)
    return result


