# cortex/server_intent_parser.py

import json
from typing import Any, Dict, List
from cortex.decision_manager import IntentType

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
    if isinstance(raw_intent, IntentType):
        return raw_intent
    if isinstance(raw_intent, str):
        return _INTENT_STR_MAP.get(raw_intent.lower(), IntentType.OBSERVE)
    return IntentType.OBSERVE

def _ensure_list(value: Any) -> List:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]

def parse_server_intent(raw_server_response: Any) -> Dict[str, Any]:
    if isinstance(raw_server_response, dict):
        server = raw_server_response
    else:
        try:
            server = json.loads(raw_server_response)
        except Exception:
            server = {}

    return {
        "intent": _map_intent(server.get("intent")),
        "behavior": server.get("behavior"),
        "speech_suggestions": _ensure_list(server.get("speech_suggestions")),
        "nonverbal_suggestions": server.get("nonverbal_suggestions", {}),
        "memory_updates": _ensure_list(server.get("memory_updates")),
        "world_updates": _ensure_list(server.get("world_updates")),
        "actions": _ensure_list(server.get("actions")),
    }
