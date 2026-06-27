from crawler.pwm import PWM
from crawler.pin import Pin
import time


class Searchlight:
    """Minimal driver using MotorPort (PWM + DIR pin)."""

    def __init__(self, pwm_pin="P13", dir_pin="D4", freq=100):
        # Hardware objects
        self.pwm = PWM(pwm_pin)
        self.dir = Pin(dir_pin)

        # Internal state
        self.freq = freq
        self._brightness = 0

        # Direction pin is always ON for a light
        self.dir.value(True)

        # PWM setup
        self.pwm.period(4095)
        self.pwm.prescaler(10)
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
    print("[Test] Initializing Searchlight on Motor Port 1 (P13/D4)...")
    led = Searchlight(pwm_pin="P13", dir_pin="D4")

    print("[Test] Setting brightness to 10%")
    led.brightness = 10
    time.sleep(2)

    print("[Test] Setting brightness to 100%")
    led.brightness = 100
    time.sleep(2)

    print("[Test] Turning off")
    led.brightness = 0
