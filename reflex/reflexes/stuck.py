from reflex.reflexive_layer import Reflex
from cortex.behavior_plan import BehaviorPlan

class StuckReflex(Reflex):
    priority = 80

    def should_trigger(self, sensor_state, world_state, hardware_state):
        commanded = hardware_state.status.get("motion", {}).get("commanded_delta")
        la_mag = sensor_state.get("linear_accel_mag")

        if commanded is None or la_mag is None:
            return False

        # If commanded movement is significant but actual movement is tiny
        return commanded > 0.1 and la_mag < commanded * 0.2

    def return_plan(self, sensor_state, world_state, hardware_state):
        plan = BehaviorPlan()

        plan.actions.append({"category": "full-body", "type": "stop"})
        plan.nonverbal.setdefault("sounds", [])
        plan.nonverbal["sounds"].append({"category": "help"})

        return plan
