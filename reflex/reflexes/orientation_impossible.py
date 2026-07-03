from reflex.reflexive_layer import Reflex
from cortex.behavior_plan import BehaviorPlan

class OrientationImpossibleReflex(Reflex):
    priority = 999

    def should_trigger(self, perception, world_state, internal_state, hardware_state):
        tilt = perception.get("imu", {}).get("tilt_deg")
        roll = perception.get("imu", {}).get("roll_deg")
        pitch = perception.get("imu", {}).get("pitch_deg")

        if tilt is None:
            return False

        return tilt > 70 or abs(roll) > 70 or abs(pitch) > 70

    def execute(self):
        plan = BehaviorPlan()

        plan.actions.append({"category": "full-body", "type": "stop"})
        plan.nonverbal["expression"].append({"mood": "alarmed"})
        plan.nonverbal["sounds"].append({"category": "alert"})

        return 