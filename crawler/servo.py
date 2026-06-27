#!/usr/bin/env python3
from crawler.pwm import PWM
from crawler.utils import mapping


class Servo(PWM):
    """Servo motor class"""

    MAX_PW = 2500
    MIN_PW = 500
    FREQ = 50
    PERIOD = 4095

    def __init__(self, channel, address=None, *args, **kwargs):
        """
        Initialize the servo motor class.

        :param channel: PWM channel number (0–14 / P0–P14)
        """
        super().__init__(channel, address, *args, **kwargs)
        self.period(self.PERIOD)
        prescaler = self.CLOCK / self.FREQ / self.PERIOD
        self.prescaler(prescaler)
        self._angle = 0.0

    # ------------------------------
    # Angle property
    # ------------------------------

    @property
    def angle(self) -> float:
        """Current servo angle in degrees."""
        return self._angle

    @angle.setter
    def angle(self, value: float) -> None:
        """Set servo angle (-90 to 90 degrees)."""
        if not isinstance(value, (int, float)):
            raise ValueError(f"Angle must be int or float, not {type(value)}")

        # Clamp
        value = max(-90, min(90, value))
        self._angle = float(value)

        self._debug(f"Set angle to: {value}")

        pulse_width = mapping(value, -90, 90, self.MIN_PW, self.MAX_PW)
        self._debug(f"Pulse width: {pulse_width}")

        self._set_pulse_width_time(pulse_width)

    # ------------------------------
    # Internal pulse width handler
    # ------------------------------

    def _set_pulse_width_time(self, pulse_width_time: float) -> None:
        """Convert pulse width (µs) to PCA9685 ticks."""
        pulse_width_time = max(self.MIN_PW, min(self.MAX_PW, pulse_width_time))

        pwr = pulse_width_time / 20000
        self._debug(f"pulse width rate: {pwr}")

        value = int(pwr * self.PERIOD)
        self._debug(f"pulse width value: {value}")

        self.pulse_width(value)
