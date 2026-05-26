from kernel.reflexive_layer import Reflex


class StuckReflex(Reflex):
    priority = 80

    def should_trigger(self, perception, world_state, internal_state):
        imu = perception["imu"]
        accel = imu["accel"]

        # crude: if commanded to move but accel is near zero
        if internal_state.commanded_motion and abs(accel[0]) < 0.01 and abs(accel[1]) < 0.01:
            return True

        return False

    def execute(self):
        return {"intent": "request_help_stuck"}
