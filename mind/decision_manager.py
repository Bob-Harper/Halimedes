# mind/decision_manager.py

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Mapping


def safe_float(value: Any) -> float | None:
    """
    Convert value to float if possible, otherwise return None.
    Use this before numeric comparisons to avoid 'None < number' errors.
    """
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
    

# ====== ENUMS / BASIC TYPES ===================================================

class IntentType(Enum):
    CONVERSE = auto()
    ACT = auto()
    IGNORE = auto()
    OBSERVE = auto()
    COMMAND = auto()
    EXPLORE = auto()
    IDLE = auto()
    INTERNAL = auto()
        
@dataclass
class Perception:
    """Pi-side perception snapshot for this tick."""
    user_text: Optional[str] = None
    user_emotion: Optional[str] = None
    speaker: Optional[str] = None
    audio_direction: Optional[str] = None  # e.g. "left", "right", "front"
    faces: List[Dict[str, Any]] = field(default_factory=list)
    objects: List[Dict[str, Any]] = field(default_factory=list)
    qr_codes: List[Dict[str, Any]] = field(default_factory=list)
    battery_level: Optional[float] = None
    posture: Optional[str] = None
    last_action: Optional[str] = None


@dataclass
class ServerIntent:
    """Unified server response (semantic, not motor)."""
    intent: IntentType
    speech_suggestions: List[Dict[str, Any]] = field(default_factory=list)
    nonverbal_suggestions: Dict[str, Any] = field(default_factory=dict)
    memory_updates: List[Dict[str, Any]] = field(default_factory=list)
    world_updates: List[Dict[str, Any]] = field(default_factory=list)
    raw_payload: Dict[str, Any] = field(default_factory=dict)  # full JSON if needed


@dataclass
class BehaviorPlan:
    """What the body should actually do this tick."""
    # Speech: list of utterances with optional emotion
    speech: List[Dict[str, Any]] = field(default_factory=list)

    # Nonverbal: gaze, expressions, actions, sounds
    nonverbal: Dict[str, List[Dict[str, Any]]] = field(default_factory=lambda: {
        "gaze": [],
        "expression": [],
        "actions": [],
        "sounds": [],
    })

    # Memory / world-state updates
    memory: Dict[str, List[Dict[str, Any]]] = field(default_factory=lambda: {
        "write": [],
    })
    world_state: Dict[str, List[Dict[str, Any]]] = field(default_factory=lambda: {
        "update": [],
    })

    # Meta
    priority: str = "normal"          # "low" | "normal" | "high"
    should_interrupt: bool = False    # can this preempt current behavior?


# ====== INTERNAL STATE MANAGERS ===============================================

@dataclass
class WorldState:
    """Persistent model of the external world."""
    location: Optional[str] = None
    known_people: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    last_speaker: Optional[str] = None
    last_user_emotion: Optional[str] = None
    environment: Dict[str, Any] = field(default_factory=dict)  # map, anchors, etc.


@dataclass
class InternalState:
    """Persistent model of Hal's internal condition."""
    mood: str = "neutral"
    engagement: float = 0.5   # 0–1
    fatigue: float = 0.0      # 0–1
    curiosity: float = 0.5    # 0–1
    current_activity: str = "idle"  # "idle", "engaged", "exploring", etc.
    last_action: Optional[str] = None


@dataclass
class Goals:
    """Short/medium/long-term goals."""
    short_term: List[Dict[str, Any]] = field(default_factory=list)
    medium_term: List[Dict[str, Any]] = field(default_factory=list)
    long_term: List[Dict[str, Any]] = field(default_factory=list)


# ====== DECISION MANAGER ======================================================

class DecisionManager:
    """
    Central brain: takes perception + server intent, produces a BehaviorPlan.
    """

    def __init__(self) -> None:
        self.world_state = WorldState()
        self.internal_state = InternalState()
        self.goals = Goals()

    # -------------------------------------------------------------------------
    # PUBLIC ENTRYPOINT
    # -------------------------------------------------------------------------
    def decide(self, perception: dict, server_intent: dict) -> BehaviorPlan:
        """
        Main decision function called each tick/turn.
        """
        # 1. Update world & internal state from perception
        self._update_world_state(perception)
        self._update_internal_state(perception)

        # 2. Interpret intent in context
        effective_intent = self._interpret_intent(perception, server_intent)

        # 3. Possibly update goals based on intent
        self._update_goals(effective_intent, perception, server_intent)

        # 4. Plan behavior (speech + nonverbal + memory/world updates)
        plan = self._plan_behavior(effective_intent, perception, server_intent)

        # 5. Apply safety / constraints
        self._apply_safety(plan, perception)

        # 6. Update internal bookkeeping from plan
        self._post_plan_update(plan)

        return plan

    # -------------------------------------------------------------------------
    # STATE UPDATES
    # -------------------------------------------------------------------------
    def _update_world_state(self, perception: Mapping[str, Any]) -> None:
        """Ingest perception into world_state."""
        speaker = perception.get("speaker")
        if speaker is not None:
            self.world_state.last_speaker = speaker

        emotion = perception.get("user_emotion")
        if emotion is not None:
            self.world_state.last_user_emotion = emotion

        # TODO: integrate faces, objects, qr_codes, location, etc.

    def _update_internal_state(self, perception: Mapping[str, Any]) -> None:
        """Update internal mood/engagement/fatigue/etc."""
        # Simple placeholder logic; expand later.
        if perception.get("user_emotion") == "happy":
            self.internal_state.mood = "happy"
        elif perception.get("user_emotion") == "angry":
            self.internal_state.mood = "cautious"
        # TODO: drift mood, adjust engagement, fatigue, curiosity, etc.
        self.internal_state.last_action = perception.get("last_action") or self.internal_state.last_action

    # -------------------------------------------------------------------------
    # INTENT INTERPRETATION / GOALS
    # -------------------------------------------------------------------------

    def _interpret_intent(self, perception: Mapping[str, Any], server_intent: Mapping[str, Any]) -> IntentType:
        """
        Combine server intent + local context to decide what Hal should do.
        Always returns an IntentType.
        """

        # Normalize local values
        user_text = perception.get("user_text")
        battery_raw = perception.get("battery_level")

        # Normalize server intent value
        raw_intent = server_intent.get("intent")

        # Map string → IntentType
        server_intent_enum = None
        if isinstance(raw_intent, str):
            mapping = {
                "converse": IntentType.CONVERSE,
                "act": IntentType.ACT,
                "ignore": IntentType.IGNORE,
                "observe": IntentType.OBSERVE,
                "command": IntentType.COMMAND,
                "explore": IntentType.EXPLORE,
                "idle": IntentType.IDLE,
                "internal": IntentType.INTERNAL,
            }
            server_intent_enum = mapping.get(raw_intent.lower())
        elif isinstance(raw_intent, IntentType):
            server_intent_enum = raw_intent

        # 1) If no user_text but server wants to converse, prefer OBSERVE
        if not user_text and server_intent_enum == IntentType.CONVERSE:
            return IntentType.OBSERVE

        # 2) Battery check: avoid EXPLORE/ACT when low
        if battery_raw is not None:
            try:
                if float(battery_raw) < 0.15:
                    if server_intent_enum in (IntentType.EXPLORE, IntentType.ACT):
                        return IntentType.IDLE
            except (TypeError, ValueError):
                pass

        # 3) Default: trust server intent if valid
        if server_intent_enum is not None:
            return server_intent_enum

        # Fallback
        return IntentType.OBSERVE

    def _update_goals(self, intent: IntentType, perception: Mapping[str, Any], server_intent: Mapping[str, Any]) -> None:
        """
        Adjust short/medium/long-term goals based on current intent and context.
        """
        # TODO: add real goal logic; for now, keep it minimal.
        if intent == IntentType.EXPLORE and not self.goals.short_term:
            self.goals.short_term.append({"type": "explore_area", "priority": "normal"})
            
    # -------------------------------------------------------------------------
    # BEHAVIOR PLANNING
    # -------------------------------------------------------------------------
    def _plan_behavior(self, intent: IntentType, perception: Mapping[str, Any], server_intent: Mapping[str, Any]) -> BehaviorPlan:
        """
        Turn intent + context into a concrete BehaviorPlan.
        """
        plan = BehaviorPlan()

        # Normalize plan fields
        plan.memory.setdefault("write", [])
        plan.world_state.setdefault("update", [])

        # IGNORE → do nothing
        if intent == IntentType.IGNORE:
            return plan

        # OBSERVE → apply memory/world updates only
        if intent == IntentType.OBSERVE:
            plan.memory["write"].extend(server_intent.get("memory_updates", []))
            plan.world_state["update"].extend(server_intent.get("world_updates", []))
            return plan

        # INTERNAL → same as OBSERVE but conceptually internal
        if intent == IntentType.INTERNAL:
            plan.memory["write"].extend(server_intent.get("memory_updates", []))
            plan.world_state["update"].extend(server_intent.get("world_updates", []))
            return plan

        # COMMAND → delegate to command planner
        if intent == IntentType.COMMAND:
            self._plan_command_response(plan, perception, server_intent)
            return plan

        # EXPLORE → delegate to exploration planner
        if intent == IntentType.EXPLORE:
            self._plan_exploration(plan, perception, server_intent)
            return plan

        # IDLE → idle planner
        if intent == IntentType.IDLE:
            self._plan_idle(plan, perception, server_intent)
            return plan

        # ACT → nonverbal-only planner
        if intent == IntentType.ACT:
            self._plan_nonverbal_only(plan, perception, server_intent)
            return plan

        # CONVERSE → conversation planner
        if intent == IntentType.CONVERSE:
            self._plan_conversation(plan, perception, server_intent)
            return plan

        # Fallback
        return plan    
        
    # ---- Specific planners ---------------------------------------------------

    def _plan_conversation(self, plan: BehaviorPlan, perception: Mapping[str, Any], server_intent: Mapping[str, Any]) -> None:
        """
        Build a conversational response: speech + nonverbal.
        """

        # Ensure plan fields exist
        plan.speech = plan.speech or []
        plan.nonverbal = plan.nonverbal or {}
        plan.nonverbal.setdefault("gaze", [])
        plan.nonverbal.setdefault("expression", [])
        plan.nonverbal.setdefault("actions", [])
        plan.nonverbal.setdefault("sounds", [])
        plan.memory.setdefault("write", [])
        plan.world_state.setdefault("update", [])

        # 1) Speech: server suggestions or fallback
        speech_suggestions = server_intent.get("speech_suggestions")
        if speech_suggestions:
            plan.speech.extend(speech_suggestions)
        else:
            user_text = perception.get("user_text")
            if user_text:
                plan.speech.append({
                    "text": f"I heard you say: {user_text}",
                    "emotion": self.internal_state.mood,
                })

        # 2) Nonverbal: gaze
        plan.nonverbal["gaze"].append({
            "mode": "center",
            "when": "start",
            "target": perception.get("speaker") or "unknown",
        })

        # Expression
        plan.nonverbal["expression"].append({
            "mood": self.internal_state.mood,
            "when": "during",
        })

        # Actions
        plan.nonverbal["actions"].append({
            "category": "subtle",
            "when": "after_speech",
        })

        # Sounds (optional)
        user_emotion = perception.get("user_emotion")
        if user_emotion:
            plan.nonverbal["sounds"].append({
                "category": user_emotion,
                "when": "after_speech",
            })

        # Memory/world updates
        plan.memory["write"].extend(server_intent.get("memory_updates", []))
        plan.world_state["update"].extend(server_intent.get("world_updates", []))
        
    def _plan_nonverbal_only(self, plan: BehaviorPlan, perception: Mapping[str, Any], server_intent: Mapping[str, Any]) -> None:
        """
        Nonverbal reaction only (no speech).
        """

        # Ensure plan fields exist
        plan.nonverbal = plan.nonverbal or {}
        plan.nonverbal.setdefault("actions", [])
        plan.nonverbal.setdefault("expression", [])

        # Expressive action
        plan.nonverbal["actions"].append({
            "category": "expressive",
            "when": "start",
        })

        # Matching expression
        plan.nonverbal["expression"].append({
            "mood": self.internal_state.mood,
            "when": "during",
        })
        
    def _plan_command_response(self, plan: BehaviorPlan, perception: Mapping[str, Any], server_intent: Mapping[str, Any]) -> None:
        plan.speech = plan.speech or []
        plan.nonverbal = plan.nonverbal or {}
        plan.nonverbal.setdefault("actions", [])

        user_text = perception.get("user_text", "")

        plan.speech.append({
            "text": f"Okay, {user_text}" if user_text else "Okay.",
            "emotion": "neutral"
        })

        for act in server_intent.get("actions", []):
            if isinstance(act, dict):
                plan.nonverbal["actions"].append(act)
                
    def _plan_exploration(self, plan: BehaviorPlan, perception: Mapping[str, Any], server_intent: Mapping[str, Any]) -> None:
        """
        Exploration behavior: full-body movement, gaze scanning, etc.
        """

        # Ensure plan fields exist
        plan.nonverbal = plan.nonverbal or {}
        plan.nonverbal.setdefault("actions", [])
        plan.nonverbal.setdefault("gaze", [])

        # Full-body movement
        plan.nonverbal["actions"].append({
            "category": "full-body",
            "when": "start",
        })

        # Gaze scanning
        plan.nonverbal["gaze"].append({
            "mode": "wander",
            "when": "during",
        })
        
    def _plan_idle(self, plan: BehaviorPlan, perception: Mapping[str, Any], server_intent: Mapping[str, Any]) -> None:
        """
        Idle behavior: small fidgets, subtle gaze, no speech.
        """

        plan.nonverbal = plan.nonverbal or {}
        plan.nonverbal.setdefault("actions", [])
        plan.nonverbal.setdefault("gaze", [])

        plan.nonverbal["actions"].append({
            "category": "subtle",
            "when": "start",
        })

        plan.nonverbal["gaze"].append({
            "mode": "wander",
            "when": "during",
        })


    # -------------------------------------------------------------------------
    # SAFETY / POST-PROCESSING
    # -------------------------------------------------------------------------
    def _apply_safety(self, plan: BehaviorPlan, perception: Mapping[str, Any]) -> None:
        """
        Enforce safety constraints on the plan.
        Filters out full-body actions when battery is low.
        This implementation is defensive against missing keys, non-numeric values,
        and malformed plan.nonverbal structures.
        """

        # Normalize battery value
        battery = safe_float(perception.get("battery_level"))

        # Nothing to do if battery unknown or sufficient
        if battery is None or battery >= 0.15:
            return

        # Defensive: ensure plan.nonverbal is a dict with an actions list
        nonverbal = plan.nonverbal
        if not isinstance(nonverbal, dict):
            nonverbal = {}

        actions = nonverbal.get("actions") or []
        if not isinstance(actions, list):
            actions = [actions] if actions else []

        # Filter out energy-intensive actions
        filtered = []
        for act in actions:
            if not isinstance(act, dict):
                filtered.append(act)
                continue
            if act.get("category") == "full-body":
                continue
            filtered.append(act)

        # Write back safely
        nonverbal["actions"] = filtered
        plan.nonverbal = nonverbal

        # Optional lightweight debug log
        try:
            print(f"[safety] Low battery {battery:.2f}: filtered {len(actions)-len(filtered)} full-body actions")
        except Exception:
            pass

    def _post_plan_update(self, plan: BehaviorPlan) -> None:
        """
        Update internal bookkeeping based on the chosen plan.
        """

        # Speech → engaged
        if plan.speech:
            self.internal_state.current_activity = "engaged"
            return

        # Nonverbal actions → acting
        actions = None
        if isinstance(plan.nonverbal, dict):
            actions = plan.nonverbal.get("actions")

        if actions:
            self.internal_state.current_activity = "acting"
            return

        # Otherwise → idle
        self.internal_state.current_activity = "idle"