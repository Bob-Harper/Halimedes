# cortex/behavior_manager.py

from __future__ import annotations
from typing import Optional, Dict, Any
from cortex.behavior_plan import BehaviorPlan



class BehaviorManager:
    """
    Library of reusable behavior templates.
    Turns high-level behavior names into BehaviorPlan instances.
    """

    def __init__(self):
        pass

    # ------------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------------
    def build_behavior(self, name: str, *, mood: Optional[str] = None) -> BehaviorPlan:
        """
        Given a behavior name, return a BehaviorPlan.
        """
        name = (name or "").lower().strip()

        if name == "greet":
            return self._behavior_greet(mood=mood)
        if name == "idle_fidget":
            return self._behavior_idle_fidget()
        if name == "explore":
            return self._behavior_explore()
        if name == "look_around":
            return self._behavior_look_around()

        # Fallback: empty plan
        return BehaviorPlan()

    # ------------------------------------------------------------------
    # BEHAVIOR TEMPLATES
    # ------------------------------------------------------------------
    def _behavior_greet(self, mood: Optional[str] = None) -> BehaviorPlan:
        plan = BehaviorPlan()

        # Speech
        plan.speech.append({
            "text": "Hello.",
            "emotion": mood or "neutral",
        })

        # Gaze: center on user
        plan.nonverbal["gaze"].append({
            "mode": "center",
            "when": "start",
            "target": "user",
        })

        # Expression: match mood
        plan.nonverbal["expression"].append({
            "mood": mood or "neutral",
            "when": "during",
        })

        # Subtle action
        plan.nonverbal["actions"].append({
            "category": "subtle",
            "when": "after_speech",
        })

        return plan

    def _behavior_idle_fidget(self) -> BehaviorPlan:
        plan = BehaviorPlan()

        plan.nonverbal["actions"].append({
            "category": "subtle",
            "when": "start",
        })

        plan.nonverbal["gaze"].append({
            "mode": "wander",
            "when": "during",
        })

        return plan

    def _behavior_explore(self) -> BehaviorPlan:
        plan = BehaviorPlan()

        plan.nonverbal["actions"].append({
            "category": "full-body",
            "when": "start",
        })

        plan.nonverbal["gaze"].append({
            "mode": "wander",
            "when": "during",
        })

        return plan

    def _behavior_look_around(self) -> BehaviorPlan:
        plan = BehaviorPlan()

        plan.nonverbal["gaze"].append({
            "mode": "wander",
            "when": "start",
        })

        plan.nonverbal["actions"].append({
            "category": "subtle",
            "when": "during",
        })

        return plan

    # ------------------------------------------------------------------
    # UTILS
    # ------------------------------------------------------------------
    def merge_plans(self, base: BehaviorPlan, extra: BehaviorPlan) -> BehaviorPlan:
        """
        Merge two BehaviorPlans into one.
        base is modified in-place and also returned.
        """

        # Speech
        base.speech.extend(extra.speech)

        # Nonverbal
        for key, value in extra.nonverbal.items():
            base.nonverbal.setdefault(key, [])
            base.nonverbal[key].extend(value)

        # Memory
        for key, value in extra.memory.items():
            base.memory.setdefault(key, [])
            base.memory[key].extend(value)

        # World state
        for key, value in extra.world_state.items():
            base.world_state.setdefault(key, [])
            base.world_state[key].extend(value)

        # Priority / interrupt flags (simple override)
        if extra.priority != "normal":
            base.priority = extra.priority
        if extra.should_interrupt:
            base.should_interrupt = True

        return base
