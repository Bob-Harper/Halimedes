from reflex.reflexive_layer import Reflex
from cortex.behavior_plan import BehaviorPlan

class UltrasonicReflex(Reflex):
    priority = 80   # lower than fall detection, higher than gait decisions

    def should_trigger(self, perception, world_state, internal_state, hardware_state):
        sensor_status = perception["sensor_status"]
        us = sensor_status.get("ultrasonic")

        if us is None:
            return False

        return us in ("DANGER", "TOO_CLOSE", "BAD_TOUCH")


    def execute(self, perception, world_state, internal_state, hardware_state):
        us = perception["sensor_status"]["ultrasonic"]

        plan = BehaviorPlan()

        if us == "DANGER":
            plan.actions.append({"category": "locomotion", "type": "step_back"})
            return plan

        if us == "TOO_CLOSE":
            plan.actions.append({"category": "locomotion", "type": "back_up"})
            return plan

        if us == "BAD_TOUCH":
            plan.actions.append({"category": "locomotion", "type": "back_up"})
            return plan

        return None
