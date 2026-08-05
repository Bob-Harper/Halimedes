from reflex.reflexive_layer import Reflex
from cortex.behavior_plan import BehaviorPlan

class StumbleReflex(Reflex):
    priority = 55  # lower than fall, higher than tilt

    def should_trigger(self, sensor_state, world_state, hardware_state):
        la = sensor_state.get("linear_acceleration")
        if not la:
            return False

        # horizontal jerk detection
        ax = abs(la.get("x", 0))
        ay = abs(la.get("y", 0))

        # threshold tuned for Hal's movement profile
        return ax > 2.5 or ay > 2.5

    def return_plan(self, sensor_state, world_state, hardware_state):
        plan = BehaviorPlan()

        # widen stance or shift weight
        plan.actions.append({
            "category": "locomotion",
            "type": "stabilize"
        })

        # optional nonverbal cue
        plan.nonverbal.setdefault("expression", [])
        plan.nonverbal["expression"].append({"mood": "surprised"})

        return plan
