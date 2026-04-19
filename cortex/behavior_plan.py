from dataclasses import dataclass, field
from typing import Any, Dict, List

@dataclass
class BehaviorPlan:
    speech: List[Dict[str, Any]] = field(default_factory=list)

    nonverbal: Dict[str, List[Dict[str, Any]]] = field(default_factory=lambda: {
        "gaze": [],
        "expression": [],
        "actions": [],
        "sounds": [],
    })

    memory: Dict[str, List[Dict[str, Any]]] = field(default_factory=lambda: {
        "write": [],
    })

    world_state: Dict[str, List[Dict[str, Any]]] = field(default_factory=lambda: {
        "update": [],
    })

    priority: str = "normal"
    should_interrupt: bool = False
