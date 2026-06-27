#!/usr/bin/env python3
from crawler.basic import _Basic_class
from crawler.pwm import PWM
from crawler.servo import Servo
import time
from crawler.filedb import fileDB
import os
from typing import Optional, Sequence

config_file = os.path.expanduser("~/hal/data/robot-hat.conf")
import faulthandler
faulthandler.enable()

class Robot(_Basic_class):
    """
    Robot class

    This class is for makeing a servo robot with Robot HAT

    There are servo initialization, all servo move in specific speed. servo offset and stuff. make it easy to make a robot.
    All Pi-series robot from SunFounder use this class. Check them out for more details.

    PiSloth: https://github.com/sunfounder/pisloth

    PiArm: https://github.com/sunfounder/piarm

    PiCrawler: https://github.com/sunfounder/picrawler
    """

    move_list = {}
    """Preset actions"""

    max_dps = 500  # dps, degrees per second, genally in 4.8V : 60des/0.14s, dps = 428
    # max_dps = 500 # physical hardware constraint
    """Servo max Degree Per Second"""

    def __init__(self, pin_list, db=config_file, name=None, init_angles=None, init_order=None, **kwargs):
        """
        Initialize the robot class

        :param pin_list: list of pin number[0-11]
        :type pin_list: list
        :param db: config file path
        :type db: str
        :param name: robot name
        :type name: str
        :param init_angles: list of initial angles
        :type init_angles: list
        :param init_order: list of initialization order(Servos will init one by one in case of sudden huge current, pulling down the power supply voltage. default order is the pin list. in some cases, you need different order, use this parameter to set it.)
        :type init_order: list
        :type init_angles: list
        """
        super().__init__(**kwargs)
        self.servo_list = []
        self.pin_num = len(pin_list)

        if name == None:
            self.name = 'other'
        else:
            self.name = name

        self.offset_value_name = f"{self.name}_servo_offset_list"
        # offset
        self.db = fileDB(db=db)
        raw = self.db.get(self.offset_value_name,
                        default_value=str(self.new_list(0)))
        temp_str = str(raw)
        temp = [float(i.strip()) for i in temp_str.strip("[]").split(",") if i.strip()]
        self.offset: list[float] = temp
        # parameter init
        self.servo_positions = self.new_list(0)
        self.origin_positions = self.new_list(0)
        self.calibrate_position = self.new_list(0)
        self.direction = self.new_list(1)

        # servo init
        if init_angles is None:
            init_angles = [0] * self.pin_num
        else:
            if len(init_angles) != self.pin_num:
                raise ValueError('init angles numbers do not match pin numbers ')

        if init_order == None:
            init_order = range(self.pin_num)

        for i, pin in enumerate(pin_list):
            self.servo_list.append(Servo(pin))
            self.servo_positions[i] = init_angles[i]
        for i in init_order:
            self.servo_list[i].angle(self.offset[i]+self.servo_positions[i])
            time.sleep(0.15)

        self.last_move_time = time.time()

    def new_list(self, default_value):
        """
        Create a list of servo angles with default value

        :param default_value: default value of servo angles
        :type default_value: int or float
        :return: list of servo angles
        :rtype: list
        """
        _ = [default_value] * self.pin_num
        return _

    def servo_write_raw(self, angle_list):
        """
        Set servo angles to specific raw angles

        :param angle_list: list of servo angles
        :type angle_list: list
        """
        for i in range(self.pin_num):
            self.servo_list[i].angle(angle_list[i])

    def servo_write_all(self, angles):
        """
        Set servo angles to specific angles with original angle and offset

        :param angles: list of servo angles
        :type angles: list
        """
        rel_angles = []  # ralative angle to home
        for i in range(self.pin_num):
            rel_angles.append(
                self.direction[i] * (self.origin_positions[i] + angles[i] + self.offset[i]))
        self.servo_write_raw(rel_angles)

    def servo_move(self, targets, speed=50, bpm=None):
        """
        With the higher physical DPS limit (500°/s), the logical speed scale has been
        expanded to 0-120. This preserves the original behavior where speed=100 matches
        the previous maximum speed at 428°/s, while allowing additional headroom up to
        the true hardware limit. The result is a more intuitive and linear speed control
        for the user, with speed=120 corresponding to the servo maximum achievable DPS.

        Existing coded speed values can remain unchanged. The new 0-120 scale preserves
        the original behavior where speed=100 represents the previous maximum, so all
        existing motions continue to run at their intended speeds without modification.

        Move servos to target angles with speed or bpm.

        :param targets: list of servo angles
        :type targets: list[float]
        :param speed: logical speed (0-120)
        :type speed: int or float
        :param bpm: beats per minute (optional, overrides speed)
        :type bpm: int or float
        """
        # Clamp speed
        speed = max(0, min(120, speed))

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

        # If bpm is given, use it to define total_time per move
        if bpm:
            total_time = 60.0 / bpm * 1000.0  # ms per beat
            # Derive effective dps from bpm and clamp to max_dps
            current_dps = max_delta / total_time * 1000.0
            target_dps = min(current_dps, self.max_dps)
            total_time = max_delta / target_dps * 1000.0
        else:
            # Map speed 0–120 to 0–max_dps
            target_dps = (speed / 120.0) * self.max_dps
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

    def do_action(self, motion_name, step=1, speed=50):
        """
        IS THIS EVEN USED?  PICRAWLER CLASS HAS ITS OWN THAT IS USED.  NOTE FOR POSSIBLE REMOVAL.
        Do prefix action with motion_name and step and speed

        :param motion_name: motion
        :type motion_name: str
        :param step: step of motion
        :type step: int
        :param speed: speed of motion
        :type speed: int or float
        """
        for _ in range(step):
            for motion in self.move_list[motion_name]:
                self.servo_move(motion, speed)

    def set_offset(self, offset_list):
        """
        Set offset of servo angles

        :param offset_list: list of servo angles
        :type offset_list: list
        """
        offset_list = [min(max(offset, -20), 20) for offset in offset_list]
        temp = str(offset_list)
        self.db.set(self.offset_value_name, temp)
        self.offset: list[float] = [float(x) for x in temp.strip("[]").split(",") if x.strip()]

    def calibration(self):
        """Move all servos to home position"""
        self.servo_positions = self.calibrate_position
        self.servo_write_all(self.servo_positions)

    def reset(self):
        """Reset servo to original position"""
        self.servo_positions = self.new_list(0)
        self.servo_write_all(self.servo_positions)

    def soft_reset(self):
        temp_list = self.new_list(0)
        self.servo_write_all(temp_list)
