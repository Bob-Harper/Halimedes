from reflex.reflexive_layer import Reflex
from cortex.behavior_plan import BehaviorPlan


class PickupReflex(Reflex):
    priority = 95

    def should_trigger(self, perception, world_state, hardware_state):
        event = perception.get("imu", {}).get("pickup")
        return event == 1

    def execute(self):
        plan = BehaviorPlan()

        # stop motion
        plan.actions.append({"category": "full-body", "type": "stop"})

        # optional nonverbal cues
        plan.nonverbal["expression"].append({"mood": "curious"})
        plan.nonverbal["gaze"].append({"mode": "center"})
        plan.nonverbal["sounds"].append({"category": "pickup"})

        return plan