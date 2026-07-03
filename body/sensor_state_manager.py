# body/sensor_state_manager.py
from typing import Any


class SensorStateManager:
    """
    Manages ALL external, non-vision, non-audio sensors.
    Separates:
        - DRIVER OBJECTS  (hardware interfaces)
        - STATUS VALUES   (flattened readings for perception)

    Drivers are singular objects (one IMU, one radar, etc).
    Status values are the processed outputs (lists, scalars, dicts).
    This is why the names do NOT match 1:1.
    Note that the RADAR module has been removed.  It is unlikely to be added, there is nowhere to mount one.
    """

    def __init__(self, imu_driver=None):
        # ------------------------------
        # Hardware driver objects
        # ------------------------------
        self.imu = imu_driver
        self.imu_data = None
        self.status = {
            "ultrasonic": None,
            "cliff": [],
            "imu": None,
        }
        self.ultrasonic_driver = None
        self.cliff_driver = None

    async def start(self):
        """Initialize hardware modules here when added."""
        self.update()
        return

    # ------------------------------
    # Individual sensor update helpers
    # ------------------------------

    def _update_ultrasonic(self):
        if self.ultrasonic_driver:
            try:
                return self.ultrasonic_driver.read_distance()
            except Exception:
                return None
        return None

    def _interpret_ultrasonic(self, units):
        if units is None or units < 0:
            return "NO_ECHO"
        if units < 5:
            return "BAD_TOUCH"
        if units < 7.5:
            return "TOO_CLOSE"
        if units < 15:
            return "DANGER"
        if units < 25:
            return "CAUTION"
        return "CLEAR"


    # NOT CURRENTLY IMPLEMENTED, but placeholder for future cliff sensor array
    def _update_cliff(self):
        if self.cliff_driver:
            try:
                return self.cliff_driver.read_values()
            except Exception:
                return []
        return []

    # ------------------------------
    # Main update
    # ------------------------------

    def update(self):
        # Ultrasonic
        raw = self._update_ultrasonic()
        self.status["ultrasonic"] = self._interpret_ultrasonic(raw)

        # Cliff sensors
        self.status["cliff"] = self._update_cliff()

        if self.imu:
            self.imu_data = self.imu.get_latest()
            self.status["imu"] = self.imu_data

    # ------------------------------
    # Snapshot
    # ------------------------------

    def snapshot(self):
        """Return a clean copy of all sensor readings."""
        return dict(self.status)
