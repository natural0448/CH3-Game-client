"""Per-slot request correlation, retention and post-present display confirmation."""
import copy
import time
import uuid
from dataclasses import dataclass

from client.contracts.ads import SLOTS


@dataclass(frozen=True)
class AdView:
    slot_id: str
    status: str
    message: str
    decision: dict | None
    image_bytes: bytes | None
    can_request: bool
    displayed: bool


class AdSlot:
    def __init__(self, slot_id):
        self.slot_id = slot_id
        self.clear()

    def clear(self):
        self.status = "idle"
        self.message = "게임 로그인 후 광고를 받습니다."
        self.decision = None
        self.image_bytes = None
        self.request_id = None
        self.next_request_at = 0
        self.displayed = False

    def request(self, player_id, now):
        if self.status == "pending" or now < self.next_request_at:
            return None
        self.request_id = uuid.uuid4().hex
        self.next_request_at = now + 15
        self.status, self.message = "pending", "광고를 고르는 중…"
        self.decision = self.image_bytes = None
        self.displayed = False
        return {"kind": "ad", "slot_id": self.slot_id, "request_id": self.request_id,
                "player_id": player_id}

    def accept(self, event, player_id):
        if (self.status != "pending" or event.get("request_id") != self.request_id
                or event.get("slot_id") != self.slot_id or event.get("player_id") != player_id):
            return False
        self.message = event.get("message", "광고를 확인하세요.")
        if event.get("status") != 200:
            self.status = "error"
        elif event.get("decision") is None:
            self.status = "empty"
        else:
            self.status = "ready"
            self.decision = copy.deepcopy(event["decision"])
            self.image_bytes = event.get("image_bytes")
        return True

    def view(self, now):
        return AdView(self.slot_id, self.status, self.message, copy.deepcopy(self.decision),
                      self.image_bytes, self.status != "pending" and now >= self.next_request_at,
                      self.displayed)


class AdStore:
    def __init__(self):
        self.slots = {slot: AdSlot(slot) for slot in sorted(SLOTS)}

    def reset(self):
        for slot in self.slots.values():
            slot.clear()

    def views(self, now=None):
        now = time.monotonic() if now is None else now
        return {name: slot.view(now) for name, slot in self.slots.items()}

    def mark_displayed(self, receipts):
        for name, decision_id in receipts.items():
            slot = self.slots[name]
            if slot.status == "ready" and slot.decision["decision_id"] == decision_id:
                slot.displayed = True
