#!/usr/bin/env python3
from cerebellum.pwm import PWM
from cerebellum.utils import mapping
from crawler.hal_hardware import PWM_Values, Servo_Values


class Servo(PWM):
    pwm_cfg = PWM_Values()
    servo_cfg = Servo_Values()

    def __init__(self, channel, *args, **kwargs):
        super().__init__(channel, *args, **kwargs)
        prescaler = self.pwm_cfg.PWM_CLOCK / self.pwm_cfg.PWM_DEFAULT_FREQ / self.servo_cfg.SERVO_PERIOD
        self.prescaler(prescaler)
        self._angle = 0.0


    @property
    def angle(self) -> float:
        return self._angle

    @angle.setter
    def angle(self, value: float) -> None:
        if not isinstance(value, (int, float)):
            raise ValueError(f"Angle must be int or float, not {type(value)}")

        value = max(-90, min(90, value))
        self._angle = float(value)

        pulse_width = mapping(value, -90, 90, self.servo_cfg.MIN_PW, self.servo_cfg.MAX_PW)

        self._set_pulse_width_time(pulse_width)

    def _set_pulse_width_time(self, pulse_width_time: float) -> None:
        pulse_width_time = max(self.servo_cfg.MIN_PW, min(self.servo_cfg.MAX_PW, pulse_width_time))

        pwr = pulse_width_time / self.servo_cfg.FRAME_US

        value = int(pwr * self.servo_cfg.SERVO_PERIOD)

        self.pulse_width(value)
