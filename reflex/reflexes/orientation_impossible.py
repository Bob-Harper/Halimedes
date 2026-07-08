from reflex.reflexive_layer import Reflex
from cortex.behavior_plan import BehaviorPlan

class OrientationImpossibleReflex(Reflex):
    priority = 999

    def should_trigger(self, sensor_state, world_state, hardware_state):
        tilt = sensor_state.get("imu", {}).get("tilt_deg")
        roll = sensor_state.get("imu", {}).get("roll_deg")
        pitch = sensor_state.get("imu", {}).get("pitch_deg")

        if tilt is None:
            return False

        return tilt > 70 or abs(roll) > 70 or abs(pitch) > 70

    def return_plan(self, sensor_state, world_state, hardware_state):
        plan = BehaviorPlan()

        plan.actions.append({"category": "full-body", "type": "stop"})
        plan.nonverbal["expression"].append({"mood": "alarmed"})
        plan.nonverbal["sounds"].append({"category": "alert"})

        return plan