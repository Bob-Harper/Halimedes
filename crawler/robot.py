#!/usr/bin/env python3
from crawler.basic import _Basic_class
from crawler.pwm import PWM
from crawler.servo import Servo
import time
from typing import Optional, Sequence

import faulthandler
faulthandler.enable()

class Robot(_Basic_class):
    """
    Robot class is for talking to servos through Robot HAT
    """

    move_list = {}
    """Preset actions"""

    max_dps = 720
    """
    Servo max Degree Per Second
    dps, degrees per second, genally in 4.8V : 60des/0.14s, dps = 428 is original sunfounder value based on original calculated math.
    max_dps currently constrained to 720 as a known working high speed stable value.  DPS has been observed as high as 800 but will crash the pi if used directly without ramping up first.
    Scaling speed to 200 in do_action through this: speed = max(0, min(200, speed))
    Old math dps calculations vs new math dps calculations plus higher dps means scale of 0-200 leaves call sites untouched when passing existing values calibrated as 0-100 while
    allowing for speed boosts when higher values are passed through or creating new motions that require more speed and faster reaction events.
    Observation - movements that call direct servo angle adjustments must be watched closely as they can cause voltage underruns
    especially when all servos move significantly at the same times with speeds of 25 or higher.
    """

    def __init__(self, pin_list, init_angles=None, init_order=None, **kwargs):
        """
        Initialize the robot class

        :param pin_list: list of pin number[0-11]
        :type pin_list: list
        :param init_angles: list of initial angles
        :type init_angles: list
        :param init_order: list of initialization order
            (Servos will init one by one in case of sudden huge current,
            pulling down the power supply voltage. default order is the pin list.
            in some cases, you need different order, use this parameter to set it.)
        :type init_order: list
        :type init_angles: list
        """
        super().__init__(**kwargs)
        self.pin_list = pin_list
        self.servo_list = [None] * 12
        self.pin_num = 12
        # parameter init
        self.servo_positions = self.new_list(0)
        # servo init
        if init_angles is None:
            init_angles = [0] * self.pin_num
        else:
            if len(init_angles) != self.pin_num:
                raise ValueError('init angles numbers do not match pin numbers ')

        if init_order == None:
            init_order = pin_list

        COXA_PINS = [0, 3, 6, 9]

        for i, pin in enumerate(pin_list):
            if pin in COXA_PINS:
                # Brushless coxa servos
                self.servo_list[pin] = Servo(pin, min_pw=1000, max_pw=2000)
            else:
                # Sunfounder femur/tibia servos
                self.servo_list[pin] = Servo(pin, min_pw=500, max_pw=2500)
            self.servo_positions[pin] = init_angles[i]

        for pin in init_order:
            self.servo_list[pin].angle = self.servo_positions[pin]
            time.sleep(0.15)

        self.last_move_time = time.time()

    def new_list(self, default_value):
        return [default_value] * 12

    def xx_servo_write_raw(self, angle_list):
        for pin in self.pin_list:
            self.servo_list[pin].angle = angle_list[pin]

    def servo_write_raw(self, angle_list):
        # DEBUG: show the raw payload we received
        # print(f"[SERVO_RAW IN] {angle_list}")

        try:
            # iterate and assign while logging per-pin activity
            for pin in self.pin_list:
                angle = angle_list[pin] if pin < len(angle_list) else None
                # print(f"[SERVO_RAW ASSIGN] pin={pin} angle={angle}")
                # keep the original assignment
                self.servo_list[pin].angle = angle

            # final confirmation that the function completed
            # print(f"[SERVO_RAW OUT] completed; assigned {len(self.pin_list)} pins")
        except Exception as e:
            # surface any error immediately and keep the exception short and actionable
            print(f"[SERVO_RAW ERROR] exception while writing to servos: {e}")
            raise


    def servo_write_all(self, angles):
        # round to one decimal place for consistent, compact logging
        rounded_angles = [round(a, 1) if a is not None else None for a in angles]
        # print("def servo_write_all(self, angles):", rounded_angles)
        self.servo_write_raw(rounded_angles)


    def servo_move(self, targets, speed=50, bpm=None):
        """
        With the higher physical DPS limit (720°/s), the logical speed scale has been
        expanded to 0-200. This preserves the original behavior where speed=100 matches
        the previous maximum speed at 428°/s, while allowing additional headroom up to
        the true hardware limit. The result is a more intuitive and linear speed control
        for the user, with speed=200 corresponding to the servo maximum achievable DPS.

        Existing coded speed values can remain unchanged. The new scale preserves
        the original behavior where speed=100 represents the previous maximum, so all
        existing motions continue to run close to their intended speeds without modification.
        BPM as in beats per minute, so he can synchronize his tempo to the tempo of the music.
        The bpm parameter overrides speed if both are provided, allowing for precise timing control in musical applications.
        Move servos to target angles with speed or bpm.

        :param targets: list of servo angles
        :type targets: list[float]
        :param speed: logical speed (0-200)
        :type speed: int or float
        :param bpm: beats per minute (optional, overrides speed)
        :type bpm: int or float
        """
        # Clamp speed
        speed = max(0, min(200, speed))

        step_time = 10.0  # ms
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

        # If bpm is given, use it to define total_time per move to sync movements to music.
        if bpm:
            total_time = 60.0 / bpm * 1000.0  # ms per beat
            # Derive effective dps from bpm and clamp to max_dps
            current_dps = max_delta / total_time * 1000.0
            target_dps = min(current_dps, self.max_dps)
            total_time = max_delta / target_dps * 1000.0
        else:
            # Map speed 0–200 to 0–max_dps
            target_dps = (speed / 200.0) * self.max_dps
            if target_dps <= 0:
                # No movement requested; just wait one step
                time.sleep(step_time / 1000.0)
                return
            # Enforce physical ceiling
            target_dps = min(target_dps, self.max_dps)
            total_time = max_delta / target_dps * 1000.0  # ms

        # Compute number of steps
        max_step = int(total_time / step_time)
        if max_step < 1:
            max_step = 1

        # Per-step increments
        steps = [delta[i] / float(max_step) for i in range(self.pin_num)]

        for _ in range(max_step):
            start_timer = time.time()
            delay = step_time / 1000.0

            for j in range(self.pin_num):
                # Accumulate with rounding to limit drift
                self.servo_positions[j] = round(self.servo_positions[j] + steps[j], 4)
            self.servo_write_all(self.servo_positions)

            servo_move_time = time.time() - start_timer
            delay -= servo_move_time
            if delay > 0:
                time.sleep(delay)
