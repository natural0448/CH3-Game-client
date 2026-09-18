"""Server-confirmed game state with no UI or transport dependencies."""
from dataclasses import dataclass, field
import time
import uuid

from client.contracts.game import GATHER_TILE, TRAIN_TILE, read_snapshot, read_state


@dataclass
class GameState:
    own: dict | None = None
    players: dict = field(default_factory=dict)
    pending: str | None = None
    pending_action: str | None = None
    abandoned: str | None = None
    last_sent: float = float("-inf")
    epoch: int = 0
    connected: bool = False
    has_ws_state: bool = False
    online_count: int | None = None
    snapshot_epoch: int | None = None

    @property
    def ready(self):
        return self.connected and self.own is not None and self.has_ws_state

    def online_label(self):
        if self.online_count is None:
            return "온라인 확인 중" if self.own else "온라인 —"
        stale = not self.ready or self.snapshot_epoch != self.epoch
        return f"온라인 {self.online_count}명" + (" · 마지막 정보" if stale else "")

    def command(self, action, direction=None, *, now=None):
        now = time.monotonic() if now is None else now
        if not self.ready or self.pending is not None or now - self.last_sent < 0.2:
            return None
        if action not in ("move", "gather", "train"):
            return None
        if action == "train" and (self.own["x"], self.own["y"]) != TRAIN_TILE:
            return None
        if action == "move" and direction not in ("up", "down", "left", "right"):
            return None
        command = {"type": action, "command_id": str(uuid.uuid4())}
        if action == "move":
            command["direction"] = direction
        self.pending = command["command_id"]
        self.pending_action = action
        self.last_sent = now
        return {"kind": "command", "epoch": self.epoch, "command": command}

    def cancel_submission(self):
        self.pending = None
        self.pending_action = None

    def clear(self):
        self.own = None
        self.players.clear()
        self.pending = self.abandoned = None
        self.pending_action = None
        self.online_count = self.snapshot_epoch = None
        self.has_ws_state = self.connected = False
        self.last_sent = float("-inf")

    def apply_status(self, phase, epoch):
        self.epoch = epoch
        self.connected = phase == "connected"
        abandoned = False
        if not self.connected:
            self.players = {self.own["player_id"]: self.own.copy()} if self.own else {}
            if self.pending:
                self.abandoned, self.pending = self.pending, None
                self.pending_action = None
                abandoned = True
        return abandoned

    def apply_identity(self, data):
        self.own = read_state(data)
        self.players = {self.own["player_id"]: self.own.copy()}

    def apply_snapshot(self, data, epoch):
        if epoch != self.epoch or self.own is None:
            return False
        members = read_snapshot(data)
        display = {}
        for player_id, incoming in members.items():
            if incoming["room_id"] != self.own["room_id"]:
                continue
            if player_id == self.own["player_id"]:
                display[player_id] = self.own.copy()
            else:
                previous = self.players.get(player_id)
                display[player_id] = (previous if previous and previous["version"] > incoming["version"] else incoming).copy()
        self.players = display
        self.online_count = len(display)
        self.snapshot_epoch = self.epoch
        return True

    def apply_state(self, data, epoch, first=False):
        if epoch != self.epoch:
            return {"accepted": False}
        incoming = read_state(data)
        if self.own is None or incoming["room_id"] != self.own["room_id"]:
            return {"accepted": False}
        mine = incoming["player_id"] == self.own["player_id"]
        if not mine:
            previous = self.players.get(incoming["player_id"])
            if previous is None or incoming["version"] >= previous["version"]:
                self.players[incoming["player_id"]] = incoming.copy()
            return {"accepted": True, "mine": False, "state": incoming}
        if incoming["version"] < self.own["version"]:
            return {"accepted": False}
        command_id = data.get("command_id")
        if self.pending_action == "train" and self.pending and command_id != self.pending:
            return {"accepted": False}
        self.own = incoming
        self.players[incoming["player_id"]] = incoming.copy()
        self.has_ws_state = self.connected = True
        completed_action = None
        if self.pending and command_id == self.pending:
            self.pending = None
            completed_action = self.pending_action
            self.pending_action = None
        return {"accepted": True, "mine": True, "state": incoming,
                "completed_action": completed_action, "first": first}

    def apply_error(self, command_id):
        if self.pending and command_id == self.pending:
            self.pending = None
            self.pending_action = None
            return True
        return False
