# cortex/perception_snapshot.py

from dataclasses import dataclass
from typing import List, Optional, Any, Dict

@dataclass
class PerceptionSnapshot:
    # Raw perception (from PerceptionManager)
    user_text: Optional[str]
    user_emotion: Optional[str]
    speaker: Optional[str]

    faces: List[Any]
    objects: List[Any]
    qr_codes: List[Any]

    battery_level: Optional[float]
    audio_direction: Optional[float]
    last_action: Optional[str]

    # Derived context (from ContextBuilder)
    user_present: bool
    idle_ticks: int
    battery_low: bool
    battery_critical: bool
    user_speaking: bool
    attention_target: Optional[Any]
    obstacle_near: bool
