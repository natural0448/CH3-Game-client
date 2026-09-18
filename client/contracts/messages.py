"""Queue boundary types. Values must stay JSON-like and credential-free."""
from typing import Any, TypeAlias

NetworkRequest: TypeAlias = dict[str, Any]
NetworkEvent: TypeAlias = dict[str, Any]
