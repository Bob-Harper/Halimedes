# body/sensor_state_manager.py

class SensorStateManager:
    """
    Manages ALL external, non-vision, non-audio sensors.
    Separates:
        - DRIVER OBJECTS  (hardware interfaces)
        - STATUS VALUES   (flattened readings for perception)

    Drivers are singular objects (one IMU, one radar, etc).
    Status values are the processed outputs (lists, scalars, dicts).
    This is why the names do NOT match 1:1.
    """

    def __init__(self):
        # ------------------------------
        # Flattened sensor readings
        # ------------------------------
        self.status = {
            "ultrasonic": None,
            "radar_presence": None,
            "radar_distance": None,
            "accel": None,
            "gyro": None,
            "grayscale": [],
            "cliff": [],
        }

        # ------------------------------
        # Hardware driver objects
        # (singular: one driver, many readings)
        # ------------------------------
        self.ultrasonic_driver = None
        self.radar_driver = None
        self.imu_driver = None
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

    def _update_radar(self):
        if self.radar_driver:
            try:
                return {
                    "presence": self.radar_driver.presence(),
                    "distance": self.radar_driver.distance(),
                }
            except Exception:
                return {"presence": None, "distance": None}
        return {"presence": None, "distance": None}

    def _update_imu(self):
        if self.imu_driver:
            try:
                accel = self.imu_driver.read_accel()
                gyro = self.imu_driver.read_gyro()
                return accel, gyro
            except Exception:
                return None, None
        return None, None

    def _update_grayscale(self):
        if self.grayscale_driver:
            try:
                return self.grayscale_driver.read_values()
            except Exception:
                return []
        return []

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
        self.status["ultrasonic"] = self._update_ultrasonic()

        # Radar
        radar = self._update_radar()
        self.status["radar_presence"] = radar["presence"]
        self.status["radar_distance"] = radar["distance"]

        # IMU
        accel, gyro = self._update_imu()
        self.status["accel"] = accel
        self.status["gyro"] = gyro

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
