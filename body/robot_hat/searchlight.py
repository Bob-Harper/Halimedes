from body.robot_hat.pwm import PWM
from body.robot_hat.pin import Pin
from body.robot_hat.motor import Motor  # Your Motor class module

class SimpleLightMotor:
    """
    Minimal wrapper around Motor on PWM P12, direction D5,
    only PWM speed control, fixed mode 1 or 2 depending on your hardware.
    """
    def __init__(self, freq=100):
        # Assuming mode 1 or 2 is fixed; adjust as needed
        self.freq = freq
        pwm = PWM("P12")
        dir_pin = Pin("D5")

        # Choose mode 1 or 2 according to your motor driver hardware
        self.motor = Motor(pwm, dir_pin, mode=1)  # or mode=1

        self.motor.pwm.freq(self.freq)
        self.motor.pwm.pulse_width_percent(0)

    def set_brightness(self, brightness: int):
        if not 0 <= brightness <= 100:
            raise ValueError("Brightness must be 0-100")
        # Use speed() to control duty cycle; direction fixed to forward (speed > 0)
        self.motor.speed(brightness)

    def stop(self):
        self.motor.speed(0)

# Example usage:
if __name__ == "__main__":
    import time
    motor = SimpleLightMotor()
    motor.set_brightness(50)
    time.sleep(1)
    motor.set_brightness(10)
    time.sleep(1)
    motor.stop()
