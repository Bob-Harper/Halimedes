from reflex.reflexive_layer import Reflex
from cortex.behavior_plan import BehaviorPlan

class UltrasonicReflex(Reflex):
    priority = 80

    def should_trigger(self, sensor_state, world_state, hardware_state):
        us = sensor_state.get("ultrasonic_front")
        if us is None:
            return False
        return False # Disable after all reflex tests are complete
        # return us in ("DANGER", "TOO_CLOSE", "BAD_TOUCH") # Re-enable aftr other reflexes tested

    def return_plan(self, sensor_state, world_state, hardware_state):
        us = sensor_state["ultrasonic_front"]

        plan = BehaviorPlan()

        if us == "DANGER":
            plan.actions.append({"category": "locomotion", "type": "step_back"})
            return plan

        if us == "TOO_CLOSE":
            plan.actions.append({"category": "locomotion", "type": "back_up"})
            return plan

        if us == "BAD_TOUCH":
            plan.actions.append({"category": "locomotion", "type": "brace"})
            return plan

        return None
