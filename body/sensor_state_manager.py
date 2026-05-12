# body/sensor_state_manager.py

class SensorStateManager:
    """
    This manager mirrors HardwareStateManager, but for external sensors instead of robot telemetry.
    Handles ALL non-vision, non-audio, non-hardware telemetry sensors.
    This includes:
        - ultrasonic distance
        - radar presence + distance
        - accelerometer (IMU)
        - gyroscope (IMU)
        - grayscale sensors
        - IR cliff sensors
        - any future external sensors

    All values are stored in self.status and exposed via snapshot().
    Note to self: Empty/None value placeholders will not affect anything.
    As sensors are installed and enabled, the data can immediately be fed in.
    """

    def __init__(self):
        # Unified raw sensor block
        self.status = {
            "ultrasonic": None,
            "radar_presence": None,
            "radar_distance": None,
            "accel": None,
            "gyro": None,
            "grayscale": [],
            "cliff": [],
        }

        # Hardware drivers (to be wired in later)
        self.ultrasonic = None
        self.radar = None
        self.imu = None
        self.grayscale = None
        self.cliff = None

    async def start(self):
        """
        Called by Hal.startup().
        Initialize hardware modules here when you add them.
        For now, this is a no-op.
        """
        self.update()
        return

    # ------------------------------
    # Individual sensor update helpers
    # ------------------------------

    def _update_ultrasonic(self):
        if self.ultrasonic:
            try:
                return self.ultrasonic.read_distance()
            except Exception:
                return None
        return None

    def _update_radar(self):
        if self.radar:
            try:
                return {
                    "presence": self.radar.presence(),
                    "distance": self.radar.distance(),
                }
            except Exception:
                return {"presence": None, "distance": None}
        return {"presence": None, "distance": None}

    def _update_imu(self):
        if self.imu:
            try:
                accel = self.imu.read_accel()
                gyro = self.imu.read_gyro()
                return accel, gyro
            except Exception:
                return None, None
        return None, None

    def _update_grayscale(self):
        if self.grayscale:
            try:
                return self.grayscale.read_values()
            except Exception:
                return []
        return []

    def _update_cliff(self):
        if self.cliff:
            try:
                return self.cliff.read_values()
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
