#!/usr/bin/env python3
from cerebellum.pwm import PWM
from cerebellum.servo import Servo
import time
from crawler.hal_hardware import Robot_Values, Servo_Values

class Robot:

    def __init__(self, pin_list, init_angles=None, init_order=None):
        self.robot_cfg = Robot_Values()
        self.max_dps = self.robot_cfg.MAX_DPS
        self.max_speed = self.robot_cfg.SPEED_SCALE_MAX

        self.pin_list = pin_list
        self.pin_num = self.robot_cfg.PIN_COUNT

        self.servo_list = [None] * self.pin_num
        self.servo_positions = [0] * self.pin_num

        init_angles = init_angles or [0] * self.pin_num
        if len(init_angles) != self.pin_num:
            raise ValueError("init angles numbers do not match pin numbers")

        init_order = init_order or pin_list

        for i, pin in enumerate(pin_list):
            self.servo_list[pin] = Servo(pin)
            self.servo_positions[pin] = init_angles[i]

        for pin in init_order:
            self.servo_list[pin].angle = self.servo_positions[pin]
            time.sleep(0.15)

    def servo_write_raw(self, angle_list):
        for pin in self.pin_list:
            self.servo_list[pin].angle = angle_list[pin]

    def servo_move(self, targets, speed=50):
        speed = max(0, min(self.max_speed, speed))
        step_time = self.robot_cfg.STEP_TIME_MS

        delta = [targets[i] - self.servo_positions[i] for i in range(self.pin_num)]
        max_delta = max(abs(v) for v in delta)

        if max_delta == 0:
            time.sleep(step_time / 1000.0)
            return

        target_dps = min((speed / self.max_speed) * self.max_dps, self.max_dps)
        if target_dps <= 0:
            time.sleep(step_time / 1000.0)
            return

        total_time = max_delta / target_dps * 1000.0
        max_step = max(1, int(total_time / step_time))

        steps = [v / max_step for v in delta]

        for _ in range(max_step):
            start = time.time()

            for j in range(self.pin_num):
                self.servo_positions[j] = round(self.servo_positions[j] + steps[j], 4)

            self.servo_write_raw(self.servo_positions)

            elapsed = time.time() - start
            remaining = step_time/1000.0 - elapsed
            if remaining > 0:
                time.sleep(remaining)
