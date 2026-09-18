"""Shared HTTP and game fixtures."""
import json


def player(pid=1, **changes):
    return {"type": "state", "player_id": pid, "room_id": "room-01",
            "x": 0, "y": 0, "coins": 0, "version": 0, **changes}


def action_snapshot():
    return {
        "available": True,
        "source_topic": "game.actions.v1",
        "source_kind": "bounded-kafka-snapshot",
        "raw_record_count": 12,
        "label_source": "current-display-map",
        "bounds": [{"partition": 0, "start_inclusive": 0, "end_exclusive": 12}],
        "summary": {
            "generated_at": "2026-09-17T07:24:52+00:00",
            "event_count": 10,
            "by_action": [
                {"event_type": "player.moved", "action_label": "이동", "count": 7},
                {"event_type": "player.gathered", "action_label": "개인 채집", "count": 2},
                {"event_type": "player.trained", "action_label": "개인 수련", "count": 1},
            ],
            "by_room": [{"room_id": "room-01", "count": 10}],
        },
    }


def ingest_summary():
    return {
        "available": True,
        "schema_version": 1,
        "generated_at": "2026-09-18T06:28:53+00:00",
        "source": "kafka-parquet",
        "basis": "all-collected-records",
        "record_count": 12,
        "valid_record_count": 11,
        "invalid_record_count": 1,
        "unsupported_record_count": 0,
        "event_count": 10,
        "duplicate_record_count": 1,
        "by_action": [
            {"event_type": "player.moved", "count": 7},
            {"event_type": "player.gathered", "count": 2},
            {"event_type": "player.trained", "count": 1},
        ],
        "by_room": [{"room_id": "room-01", "count": 10}],
    }


class Response:
    def __init__(self, status=200, content_type="application/json", data=None, raw=None):
        self.status = status
        self.content_type = content_type
        self.raw = raw if raw is not None else json.dumps(data).encode()
        self.content = self
        self.body_read = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return None

    async def iter_chunked(self, size):
        self.body_read = True
        yield self.raw


class Session:
    def __init__(self, response):
        self.response = response
        self.calls = []
        self.closed = False

    def request(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        return self.response
