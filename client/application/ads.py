"""Per-slot request correlation, retention and post-present display confirmation."""
import copy
import time
import uuid
from dataclasses import dataclass

from client.contracts.ads import EVENT_TYPES, SLOTS, read_ad_event


@dataclass(frozen=True)
class AdView:
    slot_id: str
    status: str
    message: str
    decision: dict | None
    image_bytes: bytes | None
    can_request: bool
    displayed: bool
    impression_pending: bool = False
    impression_ok: bool = False
    click_pending: bool = False
    click_ok: bool = False
    event_error: str = ""
    event_rejected: bool = False


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
        self.retained_until = 0
        self.image_failed = False
        self.reset_events()

    def reset_events(self):
        self.impression_pending = self.impression_ok = False
        self.click_pending = self.click_ok = False
        self.click_requested = False
        self.event_retry_at = 0
        self.event_error = ""
        self.event_rejected = False

    def can_request(self, now):
        if (self.status == "pending" or self.impression_pending or self.click_pending
                or now < self.next_request_at or now < self.retained_until):
            return False
        if self.status == "ready" and not self.event_rejected:
            if not self.displayed and not self.image_failed:
                return False
            if (self.slot_id == "village-board" and self.displayed and not self.impression_ok
                    or self.click_requested and not self.click_ok):
                return False
        return True

    def request(self, player_id, now):
        if not self.can_request(now):
            return None
        self.request_id = uuid.uuid4().hex
        self.next_request_at = now + 15
        self.status, self.message = "pending", "광고를 고르는 중…"
        self.decision = self.image_bytes = None
        self.displayed = False
        self.retained_until = 0
        self.image_failed = False
        self.reset_events()
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

    def request_event(self, event_type, player_id, now):
        if (not isinstance(event_type, str) or event_type not in EVENT_TYPES
                or self.status != "ready" or not self.displayed or not self.decision
                or self.slot_id != "village-board" or self.event_rejected
                or now < self.event_retry_at):
            return None
        if (getattr(self, event_type + "_pending") or getattr(self, event_type + "_ok")
                or (event_type == "click" and not self.impression_ok)):
            return None
        setattr(self, event_type + "_pending", True)
        if event_type == "click":
            self.click_requested = True
        self.event_error = ""
        self.message = "노출 저장 중" if event_type == "impression" else "클릭 저장 중"
        return {"kind": "ad_event", "slot_id": self.slot_id, "player_id": player_id,
                "request_id": self.request_id, "decision_id": self.decision["decision_id"],
                "event_type": event_type}

    def accept_event(self, event, player_id, now):
        kind = event.get("event_type")
        if (not isinstance(kind, str) or kind not in EVENT_TYPES or self.decision is None
                or event.get("slot_id") != self.slot_id or event.get("player_id") != player_id
                or event.get("request_id") != self.request_id
                or event.get("decision_id") != self.decision["decision_id"]
                or not getattr(self, kind + "_pending")):
            return False
        setattr(self, kind + "_pending", False)
        try:
            if event.get("kind") != "ad_event" or event.get("status") != 200:
                raise ValueError("event_failed")
            read_ad_event(event.get("ad_event"), event["decision_id"], kind)
        except ValueError:
            self.event_error = event.get("message") or "실적 저장을 확인하지 못했습니다."
            self.message = self.event_error
            self.event_rejected = bool(event.get("event_rejected"))
            if self.event_rejected:
                self.click_requested = False
                self.message = "광고 새 요청 필요"
                self.retained_until = self.next_request_at = now + 2
            else:
                self.event_retry_at = now + 2
        else:
            setattr(self, kind + "_ok", True)
            self.event_error = ""
            self.message = "노출 저장 완료 · 광고 클릭 가능" if kind == "impression" else "클릭 저장 완료"
        return True

    def view(self, now):
        return AdView(self.slot_id, self.status, self.message, copy.deepcopy(self.decision),
                      self.image_bytes, self.can_request(now),
                      self.displayed, self.impression_pending, self.impression_ok,
                      self.click_pending, self.click_ok, self.event_error, self.event_rejected)


class AdStore:
    def __init__(self):
        self.slots = {slot: AdSlot(slot) for slot in sorted(SLOTS)}

    def reset(self):
        for slot in self.slots.values():
            slot.clear()

    def views(self, now=None):
        now = time.monotonic() if now is None else now
        return {name: slot.view(now) for name, slot in self.slots.items()}

    def mark_displayed(self, receipts, now=None, failures=None):
        now = time.monotonic() if now is None else now
        for name, decision_id in (failures or {}).items():
            slot = self.slots[name]
            if slot.status == "ready" and slot.decision["decision_id"] == decision_id:
                slot.image_failed = True
        for name, decision_id in receipts.items():
            slot = self.slots[name]
            if slot.status == "ready" and slot.decision["decision_id"] == decision_id:
                if not slot.displayed:
                    slot.retained_until = now + 10
                slot.displayed = True
                slot.image_failed = False
