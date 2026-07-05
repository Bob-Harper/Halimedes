from reflex.reflexive_layer import Reflex
from cortex.behavior_plan import BehaviorPlan


class FallDetectedReflex(Reflex):
    priority = 90

    def should_trigger(self, perception, world_state, hardware_state):
        event = perception.get("imu", {}).get("fall_detected")
        return event == 1

    def execute(self):
        plan = BehaviorPlan()

        plan.actions.append({"category": "full-body", "type": "stop"})
        plan.actions.append({"category": "expressive", "type": "recover"})

        plan.nonverbal["expression"].append({"mood": "surprised"})
        plan.nonverbal["sounds"].append({"category": "fall"})

        return plan