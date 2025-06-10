from body.robot_hat.pwm import PWM
from body.robot_hat.pin import Pin
import time


class Searchlight:
    """Minimal driver using MotorPort2 (PWM12, GPIO24) only."""
    # def __init__(self, pwm_pin="P12", dir_pin="D5", freq=100):  # Motorport 2
    def __init__(self, pwm_pin="P13", dir_pin="D4", freq=100):  # Motorport 1
        self.pwm = PWM(pwm_pin)
        self.dir = Pin(dir_pin)

        self.freq = freq
        self._brightness = 0

        # INIT DIR PIN
        self.dir.value(True)

        # PWM setup
        self.pwm.period(4095)
        self.pwm.prescaler(10)
        self.pwm.freq(self.freq)
        self.pwm.pulse_width_percent(0)


    def brightness(self, value: int = 0):
        """Set brightness 0-100%. If None, returns current."""
        if value is None:
            return self._brightness

        # Clamp and store value
        value = max(0, min(100, value))
        self._brightness = value

        # MotorPort2 mode 1 only
        self.pwm.pulse_width_percent(value)
        self.dir.value(True)  # Always ON direction for light


if __name__ == "__main__":
    import time

    print("[Test] Initializing LightDriver on Motor Port 1 (P13/D4)...")
    led = Searchlight(pwm_pin="P13", dir_pin="D4")

    print("[Test] Setting brightness to 10%")
    led.brightness(10)

    time.sleep(2)

    print("[Test] Turning off")
    led.brightness(0)
