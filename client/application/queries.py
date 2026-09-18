"""Read-only query request correlation and presentation state."""
from dataclasses import dataclass, field
import time
import uuid

from client.contracts.queries import QUERY_SPECS


@dataclass
class QuerySlot:
    kind: str
    opened: bool = False
    busy: bool = False
    request_id: str | None = None
    response: dict | None = None
    page: int = 0
    last_requested_at: float = float("-inf")

    def reset(self):
        self.opened = self.busy = False
        self.request_id = None
        self.response = None
        self.page = 0
        self.last_requested_at = float("-inf")


@dataclass
class QueryStore:
    slots: dict[str, QuerySlot] = field(default_factory=lambda: {
        kind: QuerySlot(kind) for kind in QUERY_SPECS
    })

    def can_request(self, kind, *, now=None):
        if kind not in self.slots:
            return False
        now = time.monotonic() if now is None else now
        slot = self.slots[kind]
        return not slot.busy and now - slot.last_requested_at >= QUERY_SPECS[kind].minimum_interval

    def request(self, kind, player_id, *, now=None):
        if kind not in self.slots or player_id is None:
            return None
        now = time.monotonic() if now is None else now
        slot = self.slots[kind]
        spec = QUERY_SPECS[kind]
        if not self.can_request(kind, now=now):
            return None
        slot.opened = kind != "delivery"
        slot.busy = True
        slot.request_id = str(uuid.uuid4())
        slot.response = None
        slot.page = 0
        slot.last_requested_at = now
        return {"kind": kind, "request_id": slot.request_id, "player_id": player_id}

    def cancel(self, kind):
        slot = self.slots[kind]
        slot.busy = False
        slot.request_id = None
        slot.last_requested_at = float("-inf")

    def accept(self, event, player_id, *, logging_out=False):
        kind = event.get("kind")
        if kind not in self.slots:
            return False
        slot = self.slots[kind]
        if (slot.request_id is None or event.get("request_id") != slot.request_id
                or player_id is None or event.get("player_id") != player_id or logging_out):
            return False
        slot.response = {key: event.get(key) for key in ("path", "status", "json", "message")}
        slot.busy = False
        slot.request_id = None
        return True

    def close_others(self, kind):
        for other_kind, slot in self.slots.items():
            if other_kind != kind and other_kind != "delivery":
                slot.opened = False

    def turn_page(self, kind, step):
        slot = self.slots[kind]
        data = (slot.response or {}).get("json") or {}
        if kind == "analytics":
            count = max(len(data.get("by_action", [])), len(data.get("by_room", [])))
            per_page = 6
        elif kind == "history":
            count, per_page = len(data.get("events", [])), 4
        elif kind == "actions":
            count, per_page = len((data.get("summary") or {}).get("by_room", [])), 4
        else:
            return
        slot.page = max(0, min(slot.page + step, max(0, (count - 1) // per_page)))

    def reset(self):
        for slot in self.slots.values():
            slot.reset()
