from kernel.reflexive_layer import Reflex

class FallDetectedReflex(Reflex):
    priority = 90

    def should_trigger(self, perception, world_state, internal_state, hardware_state):
        sensor_status = perception["sensor_status"]
        imu = sensor_status["imu"]
        accel = imu["accel"]

        if imu is None:
            return False

        if accel is None:
            return False

        tilt_deg = abs(accel[0])
        return tilt_deg > 45

    def execute(self):
        return {"intent": "brace_for_impact"}
