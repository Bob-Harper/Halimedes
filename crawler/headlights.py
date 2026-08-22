# crawler/headlights.py

from cerebellum.pwm import PWM
from cerebellum.pin import Pin
from crawler.hal_hardware import Headlights as HeadlightsConfig
import time


class Headlights:
    """Minimal driver using MotorPort (PWM + DIR pin)."""

    def __init__(self, config=None):
        # Natively pull from your hardware configuration data class if no custom override is passed
        cfg = config if config else HeadlightsConfig()

        # Hardware objects bound dynamically to your hardware file properties
        self.pwm = PWM(cfg.motor_1_pwm_pin)
        self.dir = Pin(cfg.motor_1_dir_pin)

        # Internal state
        self.freq = 100
        self._brightness = 0

        # Direction pin is always ON for a light
        self.dir.value(True)

        # PWM setup
        self.pwm.period(cfg.period)
        self.pwm.prescaler(cfg.prescaler)
        self.pwm.freq(self.freq)
        self.pwm.pulse_width_percent(0)

    # ---------------------------------------------------------
    # Brightness property
    # ---------------------------------------------------------

    @property
    def brightness(self) -> int:
        """Current brightness (0–100%)."""
        return self._brightness

    @brightness.setter
    def brightness(self, value: int) -> None:
        """Set brightness (0–100%)."""
        value = max(0, min(100, int(value)))
        self._brightness = value

        # Apply PWM duty cycle
        self.pwm.pulse_width_percent(value)

        # Direction stays ON for light
        self.dir.value(True)


# ---------------------------------------------------------
# Standalone test
# ---------------------------------------------------------

if __name__ == "__main__":
    print("[Test] Initializing Headlight Test...")
    # Boots up cleanly, automatically reading pins from crawler/hal_hardware.py
    light = Headlights()

    print("[Test] Setting brightness to 10%")
    light.brightness = 10
    time.sleep(2)

    print("[Test] Setting brightness to 50%")
    light.brightness = 50
    time.sleep(2)

    print("[Test] Setting brightness to 100%")
    light.brightness = 100
    time.sleep(2)

    print("[Test] Turning off")
    light.brightness = 0
