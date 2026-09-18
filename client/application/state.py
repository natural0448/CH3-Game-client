"""UI-facing state that is independent of Pygame objects."""
from dataclasses import dataclass, field
from typing import Mapping


@dataclass
class LoginDraft:
    username: str = ""
    password: str = ""
    focus: str | None = "username"

    def clear(self):
        self.username = self.password = ""
        self.focus = None


@dataclass
class ApplicationState:
    phase: str = "signed_out"
    message: str = "아이디와 비밀번호를 입력해 마을에 입장하세요."
    login: LoginDraft = field(default_factory=LoginDraft)
    closing: bool = False
    stopped: bool = False
    show_api: bool = False
    api_source: str = "delivery"
    api_scroll: int = 0
    ws_messages: list[str] = field(default_factory=list)

    def remember_ws(self, message):
        self.ws_messages.append(message)
        del self.ws_messages[:-3]

    def clear_account(self):
        self.login.clear()
        self.show_api = False
        self.api_source = "delivery"
        self.api_scroll = 0
        self.ws_messages.clear()


@dataclass(frozen=True)
class LoginView:
    username: str
    password_length: int
    focus: str | None


@dataclass(frozen=True)
class ApplicationView:
    phase: str
    message: str
    closing: bool
    show_api: bool
    api_source: str
    api_scroll: int
    ws_messages: tuple[str, ...]
    login: LoginView


@dataclass(frozen=True)
class GameView:
    own: dict | None
    players: tuple[dict, ...]
    pending: str | None
    ready: bool
    has_ws_state: bool
    online_label: str


@dataclass(frozen=True)
class QueryView:
    kind: str
    opened: bool
    busy: bool
    response: dict | None
    page: int
    can_request: bool


@dataclass(frozen=True)
class ScreenModel:
    app: ApplicationView
    game: GameView
    queries: Mapping[str, QueryView]
