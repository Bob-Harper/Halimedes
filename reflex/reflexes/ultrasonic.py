from reflex.reflexive_layer import Reflex

class UltrasonicReflex(Reflex):
    priority = 80   # lower than fall detection, higher than gait decisions

    def should_trigger(self, perception, world_state, internal_state, hardware_state):
        sensor_status = perception["sensor_status"]
        us = sensor_status.get("ultrasonic")

        if us is None:
            return False

        # Only trigger on meaningful states
        # Note that the ultrasonic module is forward facing only.
        return us in ("DANGER", "TOO_CLOSE", "BAD_TOUCH")

    def execute(self):
        # Map states to intents
        # Reflex layer doesn't need the raw state; HAL's behavior layer will interpret the intent.
        return {"intent": "ultrasonic_alert"}
