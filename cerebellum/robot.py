#!/usr/bin/env python3
from cerebellum.pwm import PWM
from cerebellum.servo import Servo
import time
from crawler.hal_hardware import Robot_Values, Servo_Values

class Robot():

    move_list = {}

    def __init__(self, pin_list, init_angles=None, init_order=None, **kwargs):
        super().__init__(**kwargs)
        self.robot_cfg = Robot_Values()
        self.servo_cfg = Servo_Values()
        self.max_dps = self.robot_cfg.MAX_DPS
        self.max_speed = self.robot_cfg.SPEED_SCALE_MAX
        self.pin_list = pin_list
        self.servo_list = [None] * self.robot_cfg.SERVO_COUNT
        self.pin_num = self.robot_cfg.PIN_COUNT
        self.servo_positions = self.new_list(0)
        if init_angles is None:
            init_angles = [0] * self.pin_num
        else:
            if len(init_angles) != self.pin_num:
                raise ValueError('init angles numbers do not match pin numbers ')

        if init_order == None:
            init_order = pin_list

        for i, pin in enumerate(pin_list):
            self.servo_list[pin] = Servo(pin)
            self.servo_positions[pin] = init_angles[i]

        for pin in init_order:
            self.servo_list[pin].angle = self.servo_positions[pin]
            time.sleep(0.15)

        self.last_move_time = time.time()

    def new_list(self, default_value):
        return [default_value] * self.robot_cfg.SERVO_COUNT

    def servo_write_raw(self, angle_list):
        try:
            for pin in self.pin_list:
                angle = angle_list[pin] if pin < len(angle_list) else None
                self.servo_list[pin].angle = angle

        except Exception as e:
            print(f"[SERVO_RAW ERROR] exception while writing to servos: {e}")
            raise


    def servo_write_all(self, angles):
        rounded_angles = [round(a, 1) if a is not None else None for a in angles]
        self.servo_write_raw(rounded_angles)


    def servo_move(self, targets, speed=50):
        speed = max(0, min(self.max_speed, speed))

        step_time = self.robot_cfg.STEP_TIME_MS
        delta = []
        absdelta = []

        for i in range(self.pin_num):
            value = targets[i] - self.servo_positions[i]
            delta.append(value)
            absdelta.append(abs(value))

        max_delta = max(absdelta)
        if max_delta == 0:
            time.sleep(step_time / 1000.0)
            return

        target_dps = (speed / self.max_speed) * self.max_dps
        if target_dps <= 0:
            time.sleep(step_time / 1000.0)
            return
        target_dps = min(target_dps, self.max_dps)
        total_time = max_delta / target_dps * 1000.0
        max_step = int(total_time / step_time)
        if max_step < 1:
            max_step = 1

        steps = [delta[i] / float(max_step) for i in range(self.pin_num)]

        for _ in range(max_step):
            start_timer = time.time()
            delay = step_time / 1000.0

            for j in range(self.pin_num):
                self.servo_positions[j] = round(self.servo_positions[j] + steps[j], 4)
            self.servo_write_all(self.servo_positions)

            servo_move_time = time.time() - start_timer
            delay -= servo_move_time
            if delay > 0:
                time.sleep(delay)
