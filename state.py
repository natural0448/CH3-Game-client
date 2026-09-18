"""Main-thread state. Coordinates and rewards come exclusively from the server."""

from dataclasses import dataclass, field
import time
import uuid

WIDTH, HEIGHT, TILE = 20, 15, 32
GATHER_TILE = (2, 2)
TRAIN_TILE = (3, 2)
STATE_FIELDS = ("player_id", "room_id", "x", "y", "coins", "version")
ERROR_MESSAGES = {
    "outside_map": "마을 경계 밖으로 이동할 수 없어요.",
    "not_at_gather_tile": "채집 장소 (2, 2)로 이동해 주세요.",
    "not_at_train_tile": "개인 수련 장소 (3, 2)로 이동해 주세요.",
    "too_fast": "조금만 기다린 뒤 다시 행동해 주세요.",
    "invalid_direction": "이동 방향을 확인해 주세요.",
    "unknown_action": "지원하지 않는 행동이에요.",
    "object_required": "명령 형식을 확인해 주세요.",
}


def read_state(data):
    """Validate and whitelist state; never carry auth fields into the UI."""
    if not isinstance(data, dict) or data.get("type") != "state":
        raise ValueError("invalid_state")
    result = {key: data.get(key) for key in STATE_FIELDS}
    for key in ("player_id", "x", "y", "coins", "version"):
        if type(result[key]) is not int:
            raise ValueError("invalid_state")
    if (result["player_id"] <= 0 or not 0 <= result["x"] < WIDTH
            or not 0 <= result["y"] < HEIGHT or result["coins"] < 0
            or result["version"] < 0 or not isinstance(result["room_id"], str)
            or not 1 <= len(result["room_id"]) <= 32):
        raise ValueError("invalid_state")
    # Display metadata only; game state still uses the six server fields above.
    username = data.get("username", "")
    result["username"] = username if isinstance(username, str) and len(username) <= 150 else ""
    return result


def read_snapshot(data):
    """A complete room membership list, not a command acknowledgement."""
    players = data.get("players")
    if not isinstance(players, list) or len(players) > 20:
        raise ValueError("invalid_snapshot")
    return {player["player_id"]: player for player in map(read_state, players)}


@dataclass
class VillageState:
    phase: str = "signed_out"
    message: str = "아이디와 비밀번호를 입력해 마을에 입장하세요."
    own: dict | None = None
    players: dict = field(default_factory=dict)  # Online room members, keyed by player_id.
    pending: str | None = None
    pending_action: str | None = None
    abandoned: str | None = None
    last_sent: float = float("-inf")
    epoch: int = 0
    online_count: int | None = None
    snapshot_epoch: int | None = None
    ws_messages: list = field(default_factory=list)
    has_ws_state: bool = False
    delivery: dict | None = None
    delivery_busy: bool = False
    delivery_sent_at: float = float("-inf")
    show_delivery_api: bool = False

    def can_query_delivery(self, *, now=None):
        now = time.monotonic() if now is None else now
        return self.own is not None and self.phase not in ("logging_out", "signed_out", "stopped") and not self.delivery_busy and now - self.delivery_sent_at >= 5

    def request_delivery(self, *, now=None):
        now = time.monotonic() if now is None else now
        if not self.can_query_delivery(now=now):
            return None
        self.delivery_busy = True
        self.delivery_sent_at = now
        return {"kind": "delivery"}

    @property
    def ready(self):
        return self.phase == "connected" and self.own is not None

    @property
    def online_label(self):
        if self.online_count is None:
            return "온라인 확인 중" if self.own else "온라인 —"
        stale = not self.ready or self.snapshot_epoch != self.epoch
        return f"온라인 {self.online_count}명" + (" · 마지막 정보" if stale else "")

    def remember_ws(self, message):
        self.ws_messages.append(message)
        del self.ws_messages[:-3]

    def command(self, action, direction=None, *, now=None):
        now = time.monotonic() if now is None else now
        if not self.ready or self.pending is not None or now - self.last_sent < 0.2:
            return None
        if action not in ("move", "gather", "train"):
            return None
        if action == "train" and (not self.has_ws_state or (self.own["x"], self.own["y"]) != TRAIN_TILE):
            return None
        if action == "move" and direction not in ("up", "down", "left", "right"):
            return None
        command = {"type": action, "command_id": str(uuid.uuid4())}
        if action == "move":
            command["direction"] = direction
        self.pending = command["command_id"]
        self.pending_action = action
        self.last_sent = now
        self.message = "서버가 행동을 확인하고 있어요."
        return {"kind": "command", "epoch": self.epoch, "command": command}

    def clear_account(self):
        self.own = None
        self.players.clear()
        self.pending = self.abandoned = None
        self.pending_action = None
        self.online_count = self.snapshot_epoch = None
        self.ws_messages.clear()
        self.has_ws_state = False
        self.last_sent = float("-inf")
        self.delivery = None
        self.delivery_busy = self.show_delivery_api = False
        self.delivery_sent_at = float("-inf")

    def accept(self, event):
        kind = event.get("kind")
        if kind == "status":
            self.phase = event["phase"]
            self.epoch = event.get("epoch", self.epoch)
            self.message = event["message"]
            if self.phase != "connected":
                self.players = {self.own["player_id"]: self.own.copy()} if self.own else {}
            if self.phase != "connected" and self.pending:
                # Disconnect abandons delivery, it does NOT acknowledge the command.
                self.abandoned, self.pending = self.pending, None
                self.pending_action = None
                self.message += " 전송 중 행동은 재전송하지 않아요."
        elif kind == "identity":
            self.own = read_state(event["data"])
            self.players = {self.own["player_id"]: self.own.copy()}
        elif kind == "snapshot":
            if event.get("epoch") != self.epoch or self.own is None:
                return
            members = read_snapshot(event["data"])
            display = {}
            for player_id, incoming in members.items():
                if incoming["room_id"] != self.own["room_id"]:
                    continue
                if player_id == self.own["player_id"]:
                    display[player_id] = self.own.copy()
                else:
                    previous = self.players.get(player_id)
                    display[player_id] = (previous if previous and previous["version"] > incoming["version"]
                                          else incoming).copy()
            self.players = display  # Missing members left the room.
            self.online_count = len(display)
            self.snapshot_epoch = self.epoch
            self.remember_ws(f"snapshot · {self.own['room_id']} · {self.online_count}명")
        elif kind == "state":
            if event.get("epoch") != self.epoch:
                return
            data = event["data"]
            incoming = read_state(data)
            if self.own is None or incoming["room_id"] != self.own["room_id"]:
                return
            self.remember_ws(f"state · #{incoming['player_id']} · ({incoming['x']}, {incoming['y']}) · 동전 {incoming['coins']} · v{incoming['version']}")
            if incoming["player_id"] != self.own["player_id"]:
                previous = self.players.get(incoming["player_id"])
                if previous is None or incoming["version"] >= previous["version"]:
                    self.players[incoming["player_id"]] = incoming.copy()
                return  # Someone else's action cannot acknowledge my pending command.
            if incoming["version"] < self.own["version"]:
                return
            if self.pending_action == "train" and self.pending and data.get("command_id") != self.pending:
                return  # A different response cannot confirm this training reward.
            self.own = incoming
            self.has_ws_state = True
            self.players[incoming["player_id"]] = incoming.copy()
            self.phase = "connected"
            if self.pending and data.get("command_id") == self.pending:
                self.pending = None
                trained = self.pending_action == "train"
                self.pending_action = None
                self.message = "수련 완료 · 동전 1 획득" if trained else "서버가 상태를 확정했어요."
            elif event.get("first"):
                self.message = "서버 상태를 받았어요. 방향키 또는 버튼으로 이동하세요."
        elif kind == "error" and event.get("epoch") == self.epoch:
            if self.pending and event.get("command_id") == self.pending:
                self.pending = None
                self.pending_action = None
            code = event.get("code")
            self.message = ERROR_MESSAGES.get(code, "서버가 행동을 거절했어요.")
            self.remember_ws("error · " + self.message)
        elif kind == "delivery":
            if self.own is None or event.get("player_id") != self.own["player_id"] or self.phase == "logging_out":
                return
            self.delivery_busy = False
            self.delivery = {key: event[key] for key in ("path", "status", "json", "message")}
        elif kind == "notice":
            self.message = event["message"]
        elif kind in ("logged_out", "login_failed"):
            self.clear_account()
            self.phase = "signed_out"
            self.message = event["message"]
        elif kind == "stopped":
            self.clear_account()
            self.phase = "stopped"
