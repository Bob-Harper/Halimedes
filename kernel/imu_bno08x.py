# hal/kernel/imu_bno08x.py

import time
import board
import busio

from adafruit_bno08x.i2c import BNO08X_I2C
from adafruit_bno08x import (
    BNO_REPORT_ACCELEROMETER,
    BNO_REPORT_GYROSCOPE,
    BNO_REPORT_ROTATION_VECTOR,
)

class IMU:
    def __init__(self, address=0x4B, rate_hz=50):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.sensor = BNO08X_I2C(self.i2c, address=address)

        interval_us = int(1_000_000 / rate_hz)

        # Enable SH‑2 features
        self.sensor.enable_feature(BNO_REPORT_ACCELEROMETER, report_interval=interval_us)
        self.sensor.enable_feature(BNO_REPORT_GYROSCOPE, report_interval=interval_us)
        self.sensor.enable_feature(BNO_REPORT_ROTATION_VECTOR, report_interval=interval_us)

        # Let the IMU settle
        time.sleep(0.1)

    def read(self):
        """Return a dict of all IMU data for the robot perception loop."""
        try:
            return {
                "accel": self.sensor.acceleration,     # (x, y, z)
                "gyro": self.sensor.gyro,             # (x, y, z)
                "quat": self.sensor.quaternion,       # (i, j, k, real)
                "timestamp_us": int(time.time() * 1_000_000),
            }
        except Exception:
            return None
