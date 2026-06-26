from kernel.reflexive_layer import Reflex

class StuckReflex(Reflex):
    priority = 80

    def should_trigger(self, perception, world_state, internal_state, hardware_state):
        sensor_status = perception["sensor_status"]
        imu = sensor_status["imu"]
        accel = imu["accel"]  # tuple (x, y, z)

        if imu is None:
            return False

        if accel is None:
            return False

        x, y, z = accel

        # crude: if commanded to move but accel is near zero
        if internal_state.commanded_motion and abs(x) < 0.01 and abs(y) < 0.01:
            return True

        return False

    def execute(self):
        return {"intent": "request_help_stuck"}
