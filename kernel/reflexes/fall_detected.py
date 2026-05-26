from kernel.reflexive_layer import Reflex


class FallDetectedReflex(Reflex):
    priority = 90

    def should_trigger(self, perception, world_state, internal_state):
        imu = perception["imu"]
        return imu["tilt_deg"] > 45

    def execute(self):
        return {"intent": "brace_for_impact"}
