"""Correlated read-only panel state; no Pygame or network operations."""
import uuid
from dataclasses import dataclass


@dataclass
class QueryPanel:
    kind = "analytics"
    opened: bool = False
    busy: bool = False
    response: dict | None = None
    pending: str | None = None
    page: int = 0

    def reset(self):
        self.opened = self.busy = False
        self.response = self.pending = None
        self.page = 0

    def request(self, state):
        if self.busy or state.own is None or state.phase in ("logging_out", "signed_out", "stopped"):
            return None
        self.opened = self.busy = True
        self.pending = str(uuid.uuid4())
        self.page = 0
        self.response = None
        return {"kind":self.kind, "request_id":self.pending, "player_id":state.own["player_id"]}

    def accept(self, event, state):
        if event.get("kind") in ("logged_out", "login_failed", "stopped"):
            self.reset()
        elif (event.get("kind") == self.kind and self.pending is not None
              and event.get("request_id") == self.pending and state.own is not None
              and event.get("player_id") == state.own["player_id"] and state.phase != "logging_out"):
            self.response = {key:event[key] for key in ("path", "status", "json", "message")}
            self.busy = False
            self.pending = None

