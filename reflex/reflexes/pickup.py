from reflex.reflexive_layer import Reflex
from cortex.behavior_plan import BehaviorPlan
import math

class PickupReflex(Reflex):
    priority = 70  # below fall, above stumble/tilt

    def should_trigger(self, sensor_state, world_state, hardware_state):
        g = sensor_state.get("gravity")
        la = sensor_state.get("linear_acceleration")
        gyro = sensor_state.get("gyroscope")

        if not g or not la or not gyro:
            return False

        # 1. sudden change in gravity direction
        gx, gy, gz = g["x"], g["y"], g["z"]
        mag = math.sqrt(gx*gx + gy*gy + gz*gz)
        if mag == 0:
            return False

        tilt_deg = math.degrees(math.acos(gz / mag))

        gravity_shift = tilt_deg > 20  # noticeable but not catastrophic

        # 2. upward acceleration spike
        upward = la["z"] > 2.0

        # 3. small rotational jerk (not fall-level)
        rotation = abs(gyro["x"]) > 1.0 or abs(gyro["y"]) > 1.0 or abs(gyro["z"]) > 1.0

        # pickup = controlled upward motion + orientation change
        return gravity_shift and upward and rotation

    def return_plan(self, sensor_state, world_state, hardware_state):
        plan = BehaviorPlan()

        plan.actions.append({
            "category": "locomotion",
            "type": "relax_pose"  # stop fighting the lift
        })

        plan.nonverbal.setdefault("expression", [])
        plan.nonverbal["expression"].append({"mood": "content"})

        return plan
