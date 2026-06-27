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

    def __init__(self):
        # ------------------------------
        # Flattened sensor readings
        # ------------------------------
        self.status = {
            "ultrasonic": None,
            "grayscale": [],
            "cliff": [],
        }

        # ------------------------------
        # Hardware driver objects
        # (singular: one driver, many readings)
        # ------------------------------
        self.ultrasonic_driver = None
        self.imu_driver: Any = None
        self.grayscale_driver = None
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

    def _update_imu(self):
        if self.imu_driver:
            try:
                return self.imu_driver.read()

            except Exception:
                return None
        return None

    # NOT CURRENTLY IMPLEMENTED, but placeholder for future grayscale sensor array
    def _update_grayscale(self):
        if self.grayscale_driver:
            try:
                return self.grayscale_driver.read_values()
            except Exception:
                return []
        return []

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
        """Poll all sensors and update self.status."""
        # Ultrasonic
        raw = self._update_ultrasonic()
        self.status["ultrasonic"] = self._interpret_ultrasonic(raw)

        # IMU
        self.status["imu"] = self._update_imu()

        # Grayscale
        self.status["grayscale"] = self._update_grayscale()

        # Cliff sensors
        self.status["cliff"] = self._update_cliff()

    # ------------------------------
    # Snapshot
    # ------------------------------

    def snapshot(self):
        """Return a clean copy of all sensor readings."""
        return dict(self.status)
