from reflex.reflexive_layer import Reflex
from cortex.behavior_plan import BehaviorPlan
import math

class TiltDetectorReflex(Reflex):
    priority = 60  # lower than pure tilt detector reflex

    def should_trigger(self, sensor_state, world_state, hardware_state):
        g = sensor_state.get("gravity")
        if not g:
            return False

        gx, gy, gz = g["x"], g["y"], g["z"]
        mag = math.sqrt(gx*gx + gy*gy + gz*gz)
        if mag == 0:
            return False

        tilt_deg = math.degrees(math.acos(gz / mag))

        # trigger contextual analysis if tilt is noticeable but not catastrophic
        return 15 < tilt_deg

    def return_plan(self, sensor_state, world_state, hardware_state):
        plan = BehaviorPlan()

        g = sensor_state.get("gravity")
        if not g:
            return plan

        la = sensor_state.get("linear_acceleration", {"x":0,"y":0,"z":0})

        # If linear acceleration spiked, external force caused tilt
        if abs(la["x"]) > 2 or abs(la["y"]) > 2 or abs(la["z"]) > 2:
            plan.nonverbal.setdefault("expression", [])
            plan.nonverbal["expression"].append({"mood": "surprised"})

        gx, gy, gz = g["x"], g["y"], g["z"]
        mag = math.sqrt(gx*gx + gy*gy + gz*gz)
        if mag == 0:
            return plan

        ratio = max(-1.0, min(1.0, gz / mag))
        tilt_deg = math.degrees(math.acos(ratio))

        if tilt_deg < 25:
            # Determine direction of tilt
            if gx < 0:
                plan.actions.append({"category": "locomotion", "type": "step_back"})
            elif gx > 0:
                plan.actions.append({"category": "locomotion", "type": "step_forward"})

            if abs(gy) > 1.0:
                plan.actions.append({"category": "locomotion", "type": "stretch_out"})

            return plan

        else:
            plan.actions.append({"category": "locomotion", "type": "brace"})
            return plan
