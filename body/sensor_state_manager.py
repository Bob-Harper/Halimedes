# body/sensor_state_manager.py
from typing import Any


class SensorStateManager:
    def __init__(self, imu_driver=None, ultrasonic_driver=None, cliff_driver=None):
        self.imu = imu_driver
        self.ultrasonic = ultrasonic_driver
        self.cliff = cliff_driver

        # This is the REAL sensor state going forward.
        # Flat. One field per report. No grouping.
        self.state: dict[str, Any] = {
            "game_rotation_vector": None,
            "magnetic_field": None,
            "stability_classifier": None,
            "tap_detector": None,
            "shake_detector": None,
            "flip_detector": None,
            "pickup_detector": None,
            "tilt_detector": None,
            "accelerometer": None,
            "gyroscope": None,
            "linear_acceleration": None,
            "rotation_vector": None,
            "gravity": None,

            "ultrasonic_front": None,

            "cliff_fr": None,
            "cliff_fl": None,
            "cliff_rr": None,
            "cliff_rl": None,

            "camera_frame": None,
            "camera_motion": None,
            "camera_brightness": None,
        }

    def snapshot(self):
        return dict(self.state)

    def update(self):

        # Ultrasonic
        if self.ultrasonic:
            dist = self.ultrasonic.read_distance()
            state = self.ultrasonic.interpret(dist)
            self.state["ultrasonic_front"] = state

        # Cliff sensors
        if self.cliff:
            cliff_vals = self.cliff.read_values()  # dict: fr, fl, rr, rl
            for suffix, value in cliff_vals.items():
                self.state[f"cliff_{suffix}"] = value
                
        # IMU produces multiple reports per tick
        if self.imu:
            reports = self.imu.read()

            if reports is None:
                return

            if isinstance(reports, dict):
                reports = [reports]

            for report in reports:
                rtype = report["type"]

                if rtype == "accel":
                    self.state["accelerometer"] = report

                elif rtype == "tilt":
                    self.state["tilt_detector"] = report

                elif rtype == "tap":
                    self.state["tap_detector"] = report

                elif rtype == "stability":
                    self.state["stability_classifier"] = report

                elif rtype == "shake":
                    self.state["shake_detector"] = report

                elif rtype == "rotation_vector":
                    self.state["rotation_vector"] = report

                elif rtype == "pickup":
                    self.state["pickup_detector"] = report

                elif rtype == "mag":
                    self.state["magnetic_field"] = report

                elif rtype == "linear_accel":
                    self.state["linear_acceleration"] = report

                elif rtype == "gyro":
                    self.state["gyroscope"] = report

                elif rtype == "gravity":
                    self.state["gravity"] = report

                elif rtype == "game_rotation_vector":
                    self.state["game_rotation_vector"] = report

                elif rtype == "flip":
                    self.state["flip_detector"] = report

        # Camera (placeholder)
        # camera driver will eventually push reports the same way
