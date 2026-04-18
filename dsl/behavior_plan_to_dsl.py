# dsl/behavior_plan_to_dsl.py

from typing import List
from cortex.decision_manager import BehaviorPlan


def behavior_plan_to_dsl(plan: BehaviorPlan) -> str:
    """
    Convert a BehaviorPlan into a DSL script string for MacroPlayer.
    """

    lines: List[str] = []

    # ----------------------------------------------------------------------
    # SPEECH
    # ----------------------------------------------------------------------
    for utterance in plan.speech:
        text = utterance.get("text", "")
        # emotion is ignored here because Response_Manager handles it internally
        if text:
            lines.append(f'speak "{_escape(text)}"')

    # ----------------------------------------------------------------------
    # NONVERBAL: GAZE
    # ----------------------------------------------------------------------
    for gaze in plan.nonverbal.get("gaze", []):
        mode = gaze.get("mode", "center")
        target = gaze.get("target")
        # Basic mapping: mode only for now
        if mode == "wander":
            lines.append("gaze wander")
        elif mode in ("left", "right", "up", "down", "center"):
            lines.append(f"gaze move to {mode}")
        else:
            # fallback
            lines.append("gaze move to center")

    # ----------------------------------------------------------------------
    # NONVERBAL: EXPRESSION
    # ----------------------------------------------------------------------
    for expr in plan.nonverbal.get("expression", []):
        mood = expr.get("mood", "neutral")
        lines.append(f"expression set mood {mood}")

    # ----------------------------------------------------------------------
    # NONVERBAL: ACTIONS
    # ----------------------------------------------------------------------
    for act in plan.nonverbal.get("actions", []):
        category = act.get("category")
        name = act.get("name")

        if name:
            # explicit action name
            lines.append(f"action {name}")
        elif category:
            # category-level action
            lines.append(f"action {category}")

    # ----------------------------------------------------------------------
    # NONVERBAL: SOUNDS
    # ----------------------------------------------------------------------
    for snd in plan.nonverbal.get("sounds", []):
        category = snd.get("category")
        if category:
            lines.append(f"sound {category}")

    # ----------------------------------------------------------------------
    # MEMORY + WORLD-STATE UPDATES
    # (Handled Pi-side; no DSL output)
    # ----------------------------------------------------------------------

    return "\n".join(lines)


def _escape(text: str) -> str:
    """Escape quotes for DSL safety."""
    return text.replace('"', '\\"')