from reflex.reflexive_layer import Reflex
from cortex.behavior_plan import BehaviorPlan
import math

class FallDetectedReflex(Reflex):
    priority = 80  # higher than stumble and tilt

    def should_trigger(self, sensor_state, world_state, hardware_state):
        g = sensor_state.get("gravity")
        if not g:
            return False

        gx, gy, gz = g["x"], g["y"], g["z"]
        mag = math.sqrt(gx*gx + gy*gy + gz*gz)
        if mag == 0:
            return False

        # angle from vertical
        tilt_deg = math.degrees(math.acos(gz / mag))

        # catastrophic threshold
        if tilt_deg > 45:
            return True

        # gravity collapse (robot is falling or being dropped)
        if mag < 7.0:  # normal is ~9.8 m/s^2
            return True

        return False

    def return_plan(self, sensor_state, world_state, hardware_state):
        plan = BehaviorPlan()

        # emergency brace
        plan.actions.append({
            "category": "locomotion",
            "type": "brace"
        })

        # optional nonverbal cue
        plan.nonverbal.setdefault("expression", [])
        plan.nonverbal["expression"].append({"mood": "alarmed"})

        return plan
