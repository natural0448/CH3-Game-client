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
    if data.get("source") not in ("raw", "delta", "silver"):
        raise ValueError("invalid_analytics_source")
    safe = {"available": True, "schema_version": 1,
            "generated_at": _text(data.get("generated_at"), 64),
            "source": data["source"],
            "event_count": _count(data.get("event_count"))}
    if data.get("record_count") is not None:
        safe["record_count"] = _count(data["record_count"])
    if "dataset_version" in data:
        safe["dataset_version"] = _text(data["dataset_version"])
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


def read_ingest(data):
    if not isinstance(data, dict) or type(data.get("available")) is not bool:
        raise ValueError("invalid_ingest")
    if not data["available"]:
        reason = data.get("reason")
        if reason not in ("ingest_summary_not_created", "ingest_summary_unreadable"):
            raise ValueError("invalid_ingest_reason")
        return {"available": False, "reason": reason}
    if data.get("schema_version") != 1 or data.get("source") != "kafka-parquet":
        raise ValueError("invalid_ingest_source")
    stamp = _text(data.get("generated_at"), 64)
    if datetime.fromisoformat(stamp).tzinfo is None:
        raise ValueError("invalid_ingest_time")
    result = {
        "available": True,
        "source": "kafka-parquet",
        "generated_at": stamp,
        "record_count": _count(data.get("record_count")),
        "event_count": _count(data.get("event_count")),
        "duplicate_record_count": _count(data.get("duplicate_record_count")),
        "by_action": [],
    }
    rows = data.get("by_action")
    if not isinstance(rows, list) or len(rows) > len(ACTION_TYPES):
        raise ValueError("invalid_ingest_actions")
    seen = set()
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("invalid_ingest_action")
        event_type = _text(row.get("event_type"))
        if event_type not in ACTION_TYPES or event_type in seen:
            raise ValueError("invalid_ingest_action_type")
        seen.add(event_type)
        result["by_action"].append({
            "event_type": event_type,
            "count": _count(row.get("count")),
        })
    if result["event_count"] > result["record_count"]:
        raise ValueError("invalid_ingest_event_count")
    if result["duplicate_record_count"] > result["record_count"]:
        raise ValueError("invalid_ingest_duplicate_count")
    if sum(row["count"] for row in result["by_action"]) != result["event_count"]:
        raise ValueError("invalid_ingest_action_count")
    return result


def read_windows(data):
    if not isinstance(data, dict) or type(data.get("available")) is not bool:
        raise ValueError("invalid_windows")
    if not data["available"]:
        return {"available": False, "windows": []}
    stamp = _text(data.get("generated_at"), 64)
    generated = datetime.fromisoformat(stamp)
    if generated.tzinfo is None:
        raise ValueError("invalid_windows_time")
    rows = data.get("windows")
    if not isinstance(rows, list) or len(rows) > 40:
        raise ValueError("invalid_window_rows")
    result = {"available": True, "generated_at": stamp, "windows": []}
    for row in rows:
        if not isinstance(row, dict) or row.get("kind") not in ("tumbling", "sliding"):
            raise ValueError("invalid_window_row")
        start = _text(row.get("window_start"), 64)
        end = _text(row.get("window_end"), 64)
        start_time = datetime.fromisoformat(start)
        end_time = datetime.fromisoformat(end)
        if start_time.tzinfo is None or end_time.tzinfo is None or end_time <= start_time:
            raise ValueError("invalid_window_range")
        event_type = _text(row.get("event_type"))
        if event_type not in ACTION_TYPES:
            raise ValueError("invalid_window_action")
        result["windows"].append({
            "kind": row["kind"],
            "window_start": start,
            "window_end": end,
            "event_type": event_type,
            "count": _count(row.get("count")),
        })
    return result


def _number(value, *, optional=False):
    if value is None and optional:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
        raise ValueError("invalid_number")
    return value


def _timestamp(value):
    stamp = _text(value, 64)
    if datetime.fromisoformat(stamp).tzinfo is None:
        raise ValueError("invalid_timestamp")
    return stamp


def read_lake(data):
    if (not isinstance(data, dict) or type(data.get("schema_version")) is not int
            or data["schema_version"] != 1
            or data.get("status") not in ("ready", "pending", "unavailable")):
        raise ValueError("invalid_lake")
    result = {"schema_version": 1, "status": data["status"],
              "available": data["status"] == "ready"}
    if not result["available"]:
        return result
    if (type(data.get("matched")) is not bool
            or data.get("verification_scope") != "local-and-copied-bytes"):
        raise ValueError("invalid_lake_verification")
    result.update({
        "dataset_version": _text(data.get("dataset_version")),
        "rows": _count(data.get("rows")),
        "bytes": _count(data.get("bytes")),
        "captured_at": _timestamp(data.get("captured_at")),
        "generated_at": _timestamp(data.get("generated_at")),
        "matched": data["matched"],
        "verification_scope": "local-and-copied-bytes",
    })
    return result


def read_load(data):
    if not isinstance(data, dict) or type(data.get("available")) is not bool:
        raise ValueError("invalid_load")
    if not data["available"]:
        return {"available": False, "load": None}
    source = data.get("load")
    if not isinstance(source, dict):
        raise ValueError("invalid_load_report")
    profile = source.get("profile")
    if not isinstance(profile, dict):
        raise ValueError("invalid_load_profile")
    clean_profile = {
        "clients": _count(profile.get("clients")),
        "seconds": _number(profile.get("seconds")),
        "interval_seconds": _number(profile.get("interval_seconds")),
        "players_per_room": _count(profile.get("players_per_room")),
        "asgi_processes": _count(profile.get("asgi_processes")),
    }
    clean = {
        "generated_at": _timestamp(source.get("generated_at")),
        "measurement_started_at": _timestamp(source.get("measurement_started_at")),
        "profile": clean_profile,
        "connected_success": _count(source.get("connected_success")),
        "connected_peak": _count(source.get("connected_peak")),
        "attempt_count": _count(source.get("attempt_count")),
        "success_count": _count(source.get("success_count")),
        "error_count": _count(source.get("error_count")),
        "elapsed_seconds": _number(source.get("elapsed_seconds")),
        "success_per_second": _number(source.get("success_per_second")),
        "rtt_sample_count": _count(source.get("rtt_sample_count")),
        "rtt_mean_ms": _number(source.get("rtt_mean_ms"), optional=True),
        "rtt_p95_ms": _number(source.get("rtt_p95_ms"), optional=True),
        "by_room": [],
    }
    rows = source.get("by_room")
    if not isinstance(rows, list) or len(rows) > 20:
        raise ValueError("invalid_load_rooms")
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("invalid_load_room")
        clean["by_room"].append({
            "room_id": _text(row.get("room_id")),
            "connected": _count(row.get("connected")),
            "success_count": _count(row.get("success_count")),
        })
    return {"available": True, "load": clean}


def read_metrics(data):
    if not isinstance(data, dict) or type(data.get("available")) is not bool:
        raise ValueError("invalid_metrics")
    if not data["available"]:
        return {"available": False, "metrics": None}
    source = data.get("metrics")
    if not isinstance(source, dict) or source.get("schema_version") != 1:
        raise ValueError("invalid_metrics_report")
    clean = {
        "schema_version": 1,
        "generated_at": _timestamp(source.get("generated_at")),
        "window_start": _timestamp(source.get("window_start")),
        "window_end": _timestamp(source.get("window_end")),
        "window_seconds": _count(source.get("window_seconds")),
        "confirmed_count": _count(source.get("confirmed_count")),
        "confirmed_per_second": _number(source.get("confirmed_per_second")),
        "published_recent": _count(source.get("published_recent")),
        "pending_mark_count": _count(source.get("pending_mark_count")),
        "oldest_pending_age_seconds": _number(
            source.get("oldest_pending_age_seconds"), optional=True
        ),
        "by_action": [],
        "by_room": [],
    }
    for field, key in (("by_action", "event_type"), ("by_room", "room_id")):
        rows = source.get(field)
        if not isinstance(rows, list) or len(rows) > 100:
            raise ValueError("invalid_metrics_rows")
        for row in rows:
            if not isinstance(row, dict):
                raise ValueError("invalid_metrics_row")
            clean[field].append({
                key: _text(row.get(key)),
                "count": _count(row.get("count")),
            })

    kafka = source.get("kafka")
    if not isinstance(kafka, dict) or type(kafka.get("lag_complete")) is not bool:
        raise ValueError("invalid_metrics_kafka")
    partitions = kafka.get("partitions")
    if not isinstance(partitions, list) or len(partitions) > 100:
        raise ValueError("invalid_metrics_partitions")
    clean_partitions = []
    for row in partitions:
        if not isinstance(row, dict):
            raise ValueError("invalid_metrics_partition")
        within = row.get("within_retention")
        if within is not None and type(within) is not bool:
            raise ValueError("invalid_metrics_retention")
        clean_partitions.append({
            "topic": _text(row.get("topic")),
            "partition": _count(row.get("partition")),
            "beginning_offset": _count(row.get("beginning_offset")),
            "end_offset": _count(row.get("end_offset")),
            "committed_offset": (
                None if row.get("committed_offset") is None
                else _count(row.get("committed_offset"))
            ),
            "within_retention": within,
            "lag": None if row.get("lag") is None else _count(row.get("lag")),
        })
    clean["kafka"] = {
        "topic": _text(kafka.get("topic")),
        "group_id": _text(kafka.get("group_id")),
        "partitions": clean_partitions,
        "known_lag_sum": _count(kafka.get("known_lag_sum")),
        "lag_complete": kafka["lag_complete"],
    }

    progress = source.get("spark_progress")
    if progress is None:
        clean["spark_progress"] = None
    elif isinstance(progress, dict):
        clean["spark_progress"] = {
            "id": _text(progress.get("id")),
            "runId": _text(progress.get("runId")),
            "name": _text(progress.get("name")),
            "timestamp": _timestamp(progress.get("timestamp")),
            "batchId": _count(progress.get("batchId")),
            "numInputRows": _count(progress.get("numInputRows")),
            "inputRowsPerSecond": _number(progress.get("inputRowsPerSecond")),
            "processedRowsPerSecond": _number(progress.get("processedRowsPerSecond")),
        }
    else:
        raise ValueError("invalid_metrics_progress")
    return {"available": True, "metrics": clean}


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
    "ingest": QuerySpec(
        "/api/analytics/ingest/",
        "아직 Kafka 수집 통계가 준비되지 않았어요. 수집과 집계를 마친 뒤 다시 읽어 주세요.",
        read_ingest,
    ),
    "windows": QuerySpec(
        "/api/analytics/windows/",
        "아직 창 요약이 없습니다",
        read_windows,
    ),
    "load": QuerySpec(
        "/api/analytics/load/",
        "아직 측정 전",
        read_load,
    ),
    "metrics": QuerySpec(
        "/api/analytics/metrics/",
        "아직 측정 전",
        read_metrics,
    ),
    "lake": QuerySpec(
        "/api/analytics/lake/",
        "원본 보존 검사 준비 중입니다.",
        read_lake,
    ),
    "history": QuerySpec("/api/history/", "아직 행동 기록이 없습니다", read_history),
}
