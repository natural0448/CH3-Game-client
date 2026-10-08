"""Public queues: ad selections, bounded PNG bytes and correlated event receipts.

ad_event/ad_event_error carry slot/player/request/decision/type, a validated
id/type/created receipt, needs_login for session expiry and event_rejected for
permanent refusal, as in revised day 23 period 3.
Credentials, cookies, CSRF tokens and media keys never enter results.
"""
from typing import Any, TypeAlias

NetworkRequest: TypeAlias = dict[str, Any]
NetworkEvent: TypeAlias = dict[str, Any]
