from reflex.reflexive_layer import Reflex

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

        if us == "DANGER":
            return {"category": "locomotion", "type": "step_back"}

        if us == "TOO_CLOSE":
            return {"category": "locomotion", "type": "back_up"}

        if us == "BAD_TOUCH":
            return {"category": "locomotion", "type": "back_up"}

        # fallback
        return None
