from reflex.reflexive_layer import Reflex
from cortex.behavior_plan import BehaviorPlan

class UltrasonicReflex(Reflex):
    priority = 80

    def should_trigger(self, sensor_state, world_state, hardware_state):
        us = sensor_state.get("ultrasonic_front")
        # print(f"[UltrasonicReflex] Ultrasonic sensor state: {us}")  # Debug print to verify sensor snapshot structure
        if us is None:
            return False
        return us in ("DANGER", "TOO_CLOSE", "BAD_TOUCH")

    def return_plan(self, sensor_state, world_state, hardware_state):
        us = sensor_state["ultrasonic_front"]

        plan = BehaviorPlan()

        if us == "DANGER":
            plan.actions.append({"category": "locomotion", "type": "step_back"})
            # print(f"[UltrasonicReflex] Danger detected. Plan: {plan.actions}")  # Debug print to verify plan structure
            return plan

        if us == "TOO_CLOSE":
            plan.actions.append({"category": "locomotion", "type": "back_up"})
            # print(f"[UltrasonicReflex] Too close detected. Plan: {plan.actions}")  # Debug print to verify plan structure
            return plan

        if us == "BAD_TOUCH":
            plan.actions.append({"category": "locomotion", "type": "brace"})
            # print(f"[UltrasonicReflex] Bad touch detected. Plan: {plan.actions}")  # Debug print to verify plan structure
            return plan

        return None
