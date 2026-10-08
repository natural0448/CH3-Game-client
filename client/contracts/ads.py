"""Allowlisted public advertisement fields and same-origin PNG paths."""
SLOTS = frozenset({"village-board", "lobby-banner"})
CREATIVE_PATHS = frozenset({"", "/static/ads/creatives/forest-tools.png", "/static/ads/creatives/camp-tea.png"})
EVENT_TYPES = frozenset({"impression", "click"})


def read_ad_event(data, decision_id, event_type):
    if (not isinstance(decision_id, str) or not decision_id
            or not isinstance(event_type, str) or event_type not in EVENT_TYPES
            or not isinstance(data, dict) or data.get("event_id") != decision_id + ":" + event_type
            or data.get("event_type") != event_type or type(data.get("created")) is not bool):
        raise ValueError("invalid_ad_event_response")
    return {name: data[name] for name in ("event_id", "event_type", "created")}


def read_decision(data, slot_id):
    if not isinstance(data, dict) or not isinstance(slot_id, str) or slot_id not in SLOTS:
        raise ValueError("invalid_ad")
    if data.get("ad", "selected") is None or data.get("empty") is True:
        return None
    amount = data.get("bid_amount", data.get("bid_units"))
    path = data.get("creative_path", "")
    if (data.get("slot_id") != slot_id or type(amount) is not int or not 1 <= amount <= 10000
            or not isinstance(path, str) or path not in CREATIVE_PATHS):
        raise ValueError("invalid_ad")
    result = {key: data[key] for key in ("decision_id", "campaign_id", "title", "slot_id", "policy_version")}
    if any(not isinstance(value, str) or not value for value in result.values()):
        raise ValueError("invalid_ad")
    body = data.get("body", "")
    if len(result["title"]) > 80 or not isinstance(body, str) or len(body) > 300:
        raise ValueError("invalid_ad")
    return {**result, "body": body, "creative_path": path, "bid_amount": amount}
