# mind/server_intent_parser.py
from typing import Any, Dict, List
from cortex.decision_manager import IntentType

# Map common server string intents to IntentType; extend as needed.
_INTENT_STR_MAP = {
    "converse": IntentType.CONVERSE,
    "conversation": IntentType.CONVERSE,
    "act": IntentType.ACT,
    "action": IntentType.ACT,
    "explore": IntentType.EXPLORE,
    "idle": IntentType.IDLE,
    "observe": IntentType.OBSERVE,
    "internal": IntentType.INTERNAL,
    "command": IntentType.COMMAND,
    "ignore": IntentType.IGNORE,
}

def _map_intent(raw_intent: Any) -> IntentType:
    """Return an IntentType for a raw intent value (enum or string)."""
    if isinstance(raw_intent, IntentType):
        return raw_intent
    if isinstance(raw_intent, str):
        return _INTENT_STR_MAP.get(raw_intent.lower(), IntentType.OBSERVE)
    # Unknown types fallback to OBSERVE
    return IntentType.OBSERVE

def _ensure_list(value: Any) -> List:
    """Return a list for list-like values, otherwise empty list."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    # If server returns a single item, wrap it
    return [value]

def parse_server_intent(raw_server_response: Any) -> Dict[str, Any]:
    """
    Normalize the server response into a predictable dict:
    {
      "intent": IntentType,
      "memory_updates": list,
      "world_updates": list,
      "speech": list,
      "actions": list,
      "meta": dict
    }
    """
    # Defensive: accept dict or JSON string; fall back to empty dict
    server = {}
    if isinstance(raw_server_response, dict):
        server = raw_server_response
    else:
        # try to parse JSON strings safely
        try:
            import json
            if isinstance(raw_server_response, str):
                parsed = json.loads(raw_server_response)
                if isinstance(parsed, dict):
                    server = parsed
        except Exception:
            # leave server as {}
            server = {}

    # Try to find top-level intent
    intent_raw = server.get("intent")

    # If not found, look for common wrapper keys safely
    if intent_raw is None:
        for key in ("result", "data", "response"):
            candidate = server.get(key)
            if isinstance(candidate, dict):
                # candidate is a dict, safe to access .get on it
                if candidate.get("intent") is not None:
                    intent_raw = candidate.get("intent")
                    break

    normalized = {
        "intent": _map_intent(intent_raw),
        "memory_updates": _ensure_list(server.get("memory_updates")),
        "world_updates": _ensure_list(server.get("world_updates")),
        "speech": _ensure_list(server.get("speech")),
        "actions": _ensure_list(server.get("actions")),
        "meta": {k: v for k, v in server.items() if k not in {
            "intent", "memory_updates", "world_updates", "speech", "actions"
        }}
    }

    return normalized