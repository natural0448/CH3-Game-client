"""Read-only API paths and response allowlists."""
from dataclasses import dataclass
from datetime import datetime

from client.contracts.history import read_history

ACTION_TYPES = ("player.moved", "player.gathered", "player.trained")


def _count(value):
    if type(value) is not int or value < 0:
        raise ValueError("invalid_count")
    return value


def _text(value, limit=128):
    if not isinstance(value, str) or not 1 <= len(value) <= limit or not value.isprintable():
        raise ValueError("invalid_text")
    return value


def read_delivery(data):
    if not isinstance(data, dict) or data.get("source") != "mysql-outbox":
        raise ValueError("invalid_delivery")
    return {
        "event_count": _count(data.get("event_count")),
        "pending_publish_count": _count(data.get("pending_publish_count")),
        "source": "mysql-outbox",
    }


def read_analytics(data):
    if not isinstance(data, dict) or type(data.get("available")) is not bool:
        raise ValueError("invalid_analytics")
    if not data["available"]:
        return {"available": False}
    if type(data.get("schema_version")) is not int or data["schema_version"] != 1:
        raise ValueError("invalid_analytics")
    safe = {"available": True, "schema_version": 1,
            "generated_at": _text(data.get("generated_at"), 64),
            "event_count": _count(data.get("event_count"))}
    if datetime.fromisoformat(safe["generated_at"]).tzinfo is None:
        raise ValueError("invalid_analytics_time")
    for field, key in (("by_action", "event_type"), ("by_room", "room_id")):
        rows = data.get(field)
        if not isinstance(rows, list) or len(rows) > 100:
            raise ValueError("invalid_analytics_rows")
        safe[field] = []
        for row in rows:
            if not isinstance(row, dict):
                raise ValueError("invalid_analytics_row")
            safe[field].append({key: _text(row.get(key)), "count": _count(row.get("count"))})
    return safe


def read_actions(data):
    if not isinstance(data, dict) or type(data.get("available")) is not bool:
        raise ValueError("invalid_actions")
    if not data["available"]:
        return {"available": False, "summary": None}
    if data.get("source_topic") != "game.actions.v1" or data.get("source_kind") != "bounded-kafka-snapshot":
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
        bounds = data["bounds"]
        if not isinstance(bounds, list) or len(bounds) > 100:
            raise ValueError("invalid_bounds")
        result["bounds"] = []
        for row in bounds:
            if not isinstance(row, dict):
                raise ValueError("invalid_bounds")
            bound = {key: _count(row.get(key)) for key in ("partition", "start_inclusive", "end_exclusive")}
            if bound["start_inclusive"] > bound["end_exclusive"]:
                raise ValueError("invalid_bounds")
            result["bounds"].append(bound)
    return result


@dataclass(frozen=True)
class QuerySpec:
    path: str
    empty_message: str
    parser: object
    minimum_interval: float = 0.0


QUERY_SPECS = {
    "delivery": QuerySpec("/api/delivery/", "아직 전달 상태가 없습니다", read_delivery, 5.0),
    "analytics": QuerySpec("/api/analytics/", "아직 첫 집계가 없습니다", read_analytics),
    "actions": QuerySpec("/api/analytics/actions/", "행동 집계가 아직 없습니다", read_actions),
    "history": QuerySpec("/api/history/", "아직 행동 기록이 없습니다", read_history),
}
