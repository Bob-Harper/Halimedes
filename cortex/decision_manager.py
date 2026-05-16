# cortex/decision_manager.py
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Mapping
import datetime

import asyncio
from helpers.modular_code import safe_float
from cortex.behavior_manager import BehaviorManager
from cortex.behavior_plan import BehaviorPlan
from cortex.decision_policy import DecisionPolicy


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
class ServerIntent:
    """Unified server response (semantic, not motor)."""
    intent: IntentType
    speech_suggestions: List[Dict[str, Any]] = field(default_factory=list)
    nonverbal_suggestions: Dict[str, Any] = field(default_factory=dict)
    memory_updates: List[Dict[str, Any]] = field(default_factory=list)
    world_updates: List[Dict[str, Any]] = field(default_factory=list)
    raw_payload: Dict[str, Any] = field(default_factory=dict)  # full JSON if needed


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
        self.behaviors = BehaviorManager()
        self.embedder = None
        self.semantic = None
        self.episodic = None
        self.policy = DecisionPolicy()


    # DECISION MAKER FIRST STEPS.
    def _build_state_vector(self, perception):
        # Minimal proof-of-concept
        return {
            "speaker_present": 1.0 if perception.get("speaker") else 0.0,
            "speech_detected": 1.0 if perception.get("speaker_text") else 0.0,
            "battery": safe_float(perception.get("battery_level")) or 1.0,
            "mood": 0.0 if self.internal_state.mood == "neutral" else 1.0,
            "engagement": self.internal_state.engagement,
            "curiosity": self.internal_state.curiosity,
            "fatigue": self.internal_state.fatigue,
        }

    def _interpret_intent(self, perception: Mapping[str, Any], server_intent: Mapping[str, Any]) -> IntentType:
        """
        Intent is chosen locally by the policy. The server no longer decides intent.
        """
        state = self._build_state_vector(perception)  # you said this is already wired
        policy_intent = self.policy.decide(state)

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
        return mapping.get(policy_intent, IntentType.OBSERVE)

    # -------------------------------------------------------------------------
    # Memory retrieval and integration
    # -------------------------------------------------------------------------
    def attach_memory(self, embedder, semantic, episodic):
        self.embedder = embedder
        self.semantic = semantic
        self.episodic = episodic

    def _spawn(self, coro):
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(coro)
        except RuntimeError:
            pass

    async def _store_episodic(self, text: str):
        if self.embedder is None or self.episodic is None:
            return
        vector = self.embedder.embed(text)
        await self.episodic.store(text, vector)

    async def _recall_episodic(self, text: str, perception: dict):
        if self.embedder is None or self.episodic is None:
            return
        qvec = self.embedder.embed(text)
        recall = await self.episodic.search(qvec, top_k=5)
        perception["episodic_recall"] = recall

    async def _store_semantic(self, text: str):
        if self.semantic is None:
            return
        # For now, just store under a simple key; you can make this smarter later.
        await self.semantic.write("last_utterance", text)

    async def _recall_semantic(self, text: str, perception: dict):
        if self.semantic is None:
            return
        # Example: read back that same key
        value = await self.semantic.read("last_utterance")
        perception["semantic_recall"] = value

    # -------------------------------------------------------------------------
    # PUBLIC ENTRYPOINT
    # -------------------------------------------------------------------------
    def decide(self, perception: dict, server_intent: dict) -> BehaviorPlan:
        """
        Main decision function called each tick/turn.
        """
        # MEMORY HOOKS
        text = perception.get("speaker_text")

        # Episodic memory
        if text and self.embedder and self.episodic:
            self._spawn(self._store_episodic(text))
            self._spawn(self._recall_episodic(text, perception))

        # Semantic memory
        if text and self.embedder and self.semantic:
            self._spawn(self._store_semantic(text))
            self._spawn(self._recall_semantic(text, perception))

        # Update world & internal state from perception
        self._update_world_state(perception)
        self._update_internal_state(perception)

        # Interpret intent in context
        effective_intent = self._interpret_intent(perception, server_intent)

        # Possibly update goals based on intent
        self._update_goals(effective_intent, perception, server_intent)

        # Plan behavior (speech + nonverbal + memory/world updates)
        plan = self._plan_behavior(effective_intent, perception, server_intent)

        # Apply safety / constraints
        self._apply_safety(plan, perception)

        # Update internal bookkeeping from plan
        self._post_plan_update(plan)

        return plan

    # -------------------------------------------------------------------------
    # STATE UPDATES
    # -------------------------------------------------------------------------
    def _update_world_state(self, perception):
        # Existing fields
        speaker = perception.get("speaker")
        if speaker:
            self.world_state.last_speaker = speaker

        emotion = perception.get("speaker_emotion")
        if emotion:
            self.world_state.last_user_emotion = emotion

        # NEW: faces
        faces = perception.get("faces")
        if faces:
            self.world_state.environment["faces"] = faces

        # NEW: objects
        objects = perception.get("objects")
        if objects:
            self.world_state.environment["objects"] = objects

        # NEW: QR codes
        qr = perception.get("qr_codes")
        if qr:
            self.world_state.environment["qr_codes"] = qr

        # NEW: audio direction
        direction = perception.get("audio_direction")
        if direction is not None:
            self.world_state.environment["audio_direction"] = direction

        # NEW: last action (robot’s own)
        last_action = perception.get("last_action")
        if last_action:
            self.world_state.environment["last_action"] = last_action

        if speaker:
            person = self.world_state.known_people.setdefault(speaker, {})
            person["last_seen"] = datetime.time()
            person["last_emotion"] = emotion

        # Ultrasonic
        dist = perception.get("ultrasonic_distance")
        if dist is not None:
            self.world_state.environment["ultrasonic_distance"] = dist

        # Radar
        presence = perception.get("radar_presence")
        if presence is not None:
            self.world_state.environment["radar_presence"] = presence

        radar_dist = perception.get("radar_distance")
        if radar_dist is not None:
            self.world_state.environment["radar_distance"] = radar_dist

        # Accelerometer
        accel = perception.get("accel")
        if accel:
            self.world_state.environment["accel"] = accel

        # Gyro
        gyro = perception.get("gyro")
        if gyro:
            self.world_state.environment["gyro"] = gyro

        # Grayscale
        gray = perception.get("grayscale")
        if gray:
            self.world_state.environment["grayscale"] = gray

        # Cliff sensors
        cliff = perception.get("cliff_sensors")
        if cliff:
            self.world_state.environment["cliff_sensors"] = cliff

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

        # shortcut = server_intent.get("behavior")
        # if shortcut:
        #     template = self.behaviors.build_behavior(shortcut, mood=self.internal_state.mood)
        #     return template

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
            speaker_text = perception.get("speaker_text")
            if speaker_text:
                plan.speech.append({
                    "text": f"I heard you say: {speaker_text}",
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

        speaker_text = perception.get("speaker_text", "")

        plan.speech.append({
            "text": f"Okay, {speaker_text}" if speaker_text else "Okay.",
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

