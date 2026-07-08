from reflex.reflexive_layer import Reflex
from cortex.behavior_plan import BehaviorPlan


class StuckReflex(Reflex):
    priority = 80

    def should_trigger(self, sensor_state, world_state, hardware_state):
        commanded = hardware_state.status.get("motion", {}).get("commanded_delta")
        actual = sensor_state.get("imu", {}).get("linear_accel_mag")

        if commanded is None or actual is None:
            return False

        return actual < commanded * 0.2

    def return_plan(self, sensor_state, world_state, hardware_state):
        plan = BehaviorPlan()

        plan.actions.append({"category": "full-body", "type": "stop"})
        plan.nonverbal["sounds"].append({"category": "help"})

        return plan
