"""Translate user intents and network events into owned state changes."""
import copy
import time

from client.contracts.game import ERROR_MESSAGES
from client.model.game import GameState
from client.application.queries import QueryStore
from client.application.ads import AdStore
from client.application.state import (
    ApplicationState, ApplicationView, GameView, LoginView, QueryView, ScreenModel,
)
from client.network.port import NetworkPort


class Controller:
    def __init__(self, network: NetworkPort):
        self.network = network
        self.app = ApplicationState()
        self.game = GameState()
        self.queries = QueryStore()
        self.ads = AdStore()

    def screen_model(self):
        app = ApplicationView(
            phase=self.app.phase,
            message=self.app.message,
            closing=self.app.closing,
            show_api=self.app.show_api,
            api_source=self.app.api_source,
            api_scroll=self.app.api_scroll,
            ws_messages=tuple(self.app.ws_messages),
            login=LoginView(
                username=self.app.login.username,
                password_length=len(self.app.login.password),
                focus=self.app.login.focus,
            ),
        )
        game = GameView(
            own=self.game.own.copy() if self.game.own else None,
            players=tuple(player.copy() for player in self.game.players.values()),
            pending=self.game.pending,
            ready=self.game.ready,
            has_ws_state=self.game.has_ws_state,
            online_label=self.game.online_label(),
        )
        queries = {
            kind: QueryView(
                kind=kind, opened=slot.opened, busy=slot.busy,
                response=copy.deepcopy(slot.response), page=slot.page,
                filter_value=slot.filter_value,
                can_request=self.queries.can_request(kind),
            )
            for kind, slot in self.queries.slots.items()
        }
        return ScreenModel(app=app, game=game, queries=queries, ads=self.ads.views())

    def login(self):
        draft = self.app.login
        if self.app.phase != "signed_out" or not draft.username.strip() or not draft.password:
            self.app.message = "아이디와 비밀번호를 모두 입력해 주세요."
            return
        request = {"kind": "login", "username": draft.username.strip(), "password": draft.password}
        draft.password = ""
        if self.network.submit(request):
            self.game.clear()
            self.queries.reset()
            self.ads.reset()
            self.app.phase = "authenticating"
            self.app.message = "로그인 확인 중…"
            draft.focus = None
        else:
            self.app.message = "요청 큐가 가득 찼어요. 다시 시도하세요."

    def logout(self):
        if self.game.own is not None and self.app.phase != "logging_out" and self.network.submit({"kind": "logout"}):
            self.app.phase = "logging_out"
            self.app.message = "로그아웃 확인 중…"
            self.app.login.password = ""

    def command(self, name):
        request = self.game.command(name if name in ("gather", "train") else "move", name)
        if request is None:
            return
        self.app.message = "서버가 행동을 확인하고 있어요."
        if not self.network.submit(request):
            self.game.cancel_submission()
            self.app.message = "요청 큐가 가득 찼어요. 다시 시도하세요."

    def request_query(self, kind):
        if self.game.own is None or self.app.phase in ("logging_out", "signed_out", "stopped"):
            return
        request = self.queries.request(kind, self.game.own["player_id"])
        if request is None:
            return
        self.queries.close_others(kind)
        self.app.api_source = kind
        self.app.api_scroll = 0
        if not self.network.submit(request):
            self.queries.cancel(kind)
            self.app.message = "요청 큐가 가득 찼어요. 다시 눌러 주세요."

    def request_ad(self, slot_id, now=None):
        if self.game.own is None or self.app.closing or self.app.phase in ("logging_out", "signed_out", "stopped"):
            return
        now = time.monotonic() if now is None else now
        slot = self.ads.slots[slot_id]
        request = slot.request(self.game.own["player_id"], now)
        if request and not self.network.submit(request):
            slot.status, slot.message = "error", "요청 큐가 가득 찼어요. 다시 눌러 주세요."
            slot.next_request_at = now

    def tick_ads(self):
        if (self.game.ready and self.app.phase == "connected" and not self.app.closing
                and not self.app.show_api
                and not any(slot.opened or slot.busy for slot in self.queries.slots.values())):
            for name, slot in self.ads.slots.items():
                if slot.status == "idle" or slot.status == "ready" and slot.can_request(time.monotonic()):
                    self.request_ad(name)

    def request_ad_event(self, slot_id, event_type, now=None):
        if (self.game.own is None or self.app.closing or self.app.phase != "connected"
                or not self.game.ready or self.game.pending is not None or self.app.show_api
                or any(slot.opened or slot.busy for slot in self.queries.slots.values())):
            return False
        slot = self.ads.slots.get(slot_id)
        if slot is None:
            return False
        now = time.monotonic() if now is None else now
        request = slot.request_event(event_type, self.game.own["player_id"], now)
        if request is None:
            return False
        if not self.network.submit(request):
            slot.accept_event({**request, "status": None, "message": "요청 큐가 가득 찼어요. 다시 시도하세요."},
                              self.game.own["player_id"], now)
            return False
        return True

    def confirm_ad_display(self, receipts, failures=None, now=None):
        now = time.monotonic() if now is None else now
        self.ads.mark_displayed(receipts, now=now, failures=failures)
        for name in receipts:
            self.request_ad_event(name, "impression", now=now)
            if self.ads.slots[name].click_requested:
                self.request_ad_event(name, "click", now=now)

    def handle_intent(self, intent):
        kind = intent.get("kind")
        draft = self.app.login
        if kind == "quit":
            self.app.closing = True
            draft.clear()
            self.network.stop()
        elif kind == "focus" and self.app.phase == "signed_out":
            draft.focus = intent.get("field")
        elif kind == "text" and draft.focus and self.app.phase == "signed_out":
            value = "".join(char for char in intent.get("text", "") if char.isprintable())
            if draft.focus == "username":
                draft.username = (draft.username + value)[:150]
            else:
                draft.password = (draft.password + value)[:256]
        elif kind == "backspace" and draft.focus:
            if draft.focus == "username":
                draft.username = draft.username[:-1]
            else:
                draft.password = draft.password[:-1]
        elif kind == "login":
            self.login()
        elif kind == "logout":
            self.logout()
        elif kind == "command":
            self.command(intent["action"])
        elif kind == "query":
            self.request_query(intent["query"])
        elif kind == "ad_refresh":
            self.request_ad(intent["slot_id"])
        elif kind == "ad_click":
            self.request_ad_event(intent["slot_id"], "click")
        elif kind == "panel_close":
            self.queries.slots[intent["query"]].opened = False
        elif kind == "panel_page":
            self.queries.turn_page(intent["query"], intent["step"])
        elif kind == "panel_filter":
            self.queries.set_filter(intent["query"], intent["value"])
        elif kind == "toggle_api":
            self.app.show_api = not self.app.show_api
        elif kind == "api_source":
            sources = tuple(self.queries.slots)
            self.app.api_source = sources[(sources.index(self.app.api_source) + 1) % len(sources)]
            self.app.api_scroll = 0
        elif kind == "api_scroll":
            self.app.api_scroll = max(0, self.app.api_scroll + intent["step"])

    def handle_network_event(self, event):
        kind = event.get("kind")
        if kind in ("ad_event", "ad_event_error"):
            player_id = self.game.own["player_id"] if self.game.own else None
            slot = self.ads.slots.get(event.get("slot_id"))
            if slot and self.app.phase != "logging_out":
                accepted = slot.accept_event(event, player_id, time.monotonic())
                if accepted and event.get("needs_login"):
                    # 교안의 인증 만료 처리: 현재 worker의 기존 로그아웃 경로로 정리한다.
                    self.ads.reset()
                    self.logout()
        elif kind == "ad":
            player_id = self.game.own["player_id"] if self.game.own else None
            slot = self.ads.slots.get(event.get("slot_id"))
            if slot and self.app.phase != "logging_out":
                slot.accept(event, player_id)
        elif kind == "status":
            self.app.phase = event["phase"]
            self.app.message = event["message"]
            if self.game.apply_status(event["phase"], event.get("epoch", self.game.epoch)):
                self.app.message += " 전송 중 행동은 재전송하지 않아요."
        elif kind == "identity":
            self.game.apply_identity(event["data"])
        elif kind == "snapshot":
            if self.game.apply_snapshot(event["data"], event.get("epoch")):
                self.app.remember_ws(f"snapshot · {self.game.own['room_id']} · {self.game.online_count}명")
        elif kind == "state":
            result = self.game.apply_state(event["data"], event.get("epoch"), event.get("first", False))
            if result.get("accepted"):
                incoming = result["state"]
                self.app.remember_ws(
                    f"state · #{incoming['player_id']} · ({incoming['x']}, {incoming['y']}) · 동전 {incoming['coins']} · v{incoming['version']}"
                )
            if result.get("mine"):
                self.app.phase = "connected"
                if result.get("completed_action") == "train":
                    self.app.message = "수련 완료 · 동전 1 획득"
                elif result.get("completed_action"):
                    self.app.message = "서버가 상태를 확정했어요."
                elif result.get("first"):
                    self.app.message = "서버 상태를 받았어요. 방향키 또는 버튼으로 이동하세요."
        elif kind == "error" and event.get("epoch") == self.game.epoch:
            self.game.apply_error(event.get("command_id"))
            self.app.message = ERROR_MESSAGES.get(event.get("code"), "서버가 행동을 거절했어요.")
            self.app.remember_ws("error · " + self.app.message)
        elif kind in self.queries.slots:
            player_id = self.game.own["player_id"] if self.game.own else None
            if self.queries.accept(event, player_id, logging_out=self.app.phase == "logging_out") and kind == "delivery":
                self.app.message = event.get("message", self.app.message)
        elif kind == "notice":
            self.app.message = event["message"]
        elif kind in ("logged_out", "login_failed"):
            self.game.clear()
            self.queries.reset()
            self.ads.reset()
            self.app.clear_account()
            self.app.phase = "signed_out"
            self.app.message = event["message"]
        elif kind == "stopped":
            self.game.clear()
            self.queries.reset()
            self.ads.reset()
            self.app.clear_account()
            self.app.phase = "stopped"
            self.app.stopped = True
