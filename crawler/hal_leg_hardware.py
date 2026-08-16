# crawler/hal_leg_hardware.py

class HalLegs:
    """
    Hardware Specification Matrix for Hal.
    Contains absolute physical dimensions, pin maps, and hardware zero-points.
    """
    def __init__(self):
        # Linkage dimensions (mm)
        self.COXA_LEN  = 33
        self.FEMUR_LEN = 48
        self.TIBIA_LEN = 80

        # Structural space boundaries
        self.MAX_REACH = self.FEMUR_LEN + self.TIBIA_LEN
        self.PIVOT_OFFSET = 15.0  # Vertical height of femur horn above baseplate plane
        self.FLOOR_DROP = self.MAX_REACH - self.PIVOT_OFFSET

        # Definitive leg configurations
        self.LF = {
            "name": "LF",
            "mount_x": 40, "mount_y": 40, "mount_angle": 0,
            "coxa_dir": 1, "femur_dir": 1, "tibia_dir": 1,
            "pin_coxa": 0, "pin_femur": 1, "pin_tibia": 2,
            "servo_zero_offset": 0.0,
            "joint_zero": {"coxa": 90.0, "femur": 0.0, "tibia": 0.0},
            "joint_range": {"coxa": (0, 180), "femur": (-45, 90), "tibia": (-90, 90)}
        }

        self.RF = {
            "name": "RF",
            "mount_x": 40, "mount_y": -40, "mount_angle": 0,
            "coxa_dir": 1, "femur_dir": 1, "tibia_dir": 1,
            "pin_coxa": 3, "pin_femur": 4, "pin_tibia": 5,
            "servo_zero_offset": 0.0,
            "joint_zero": {"coxa": 90.0, "femur": 5.0, "tibia": 0.0},
            "joint_range": {"coxa": (0, 180), "femur": (-45, 90), "tibia": (-90, 90)}
        }

        self.RR = {
            "name": "RR",
            "mount_x": -40, "mount_y": -40, "mount_angle": 0,
            "coxa_dir": 1, "femur_dir": 1, "tibia_dir": 1,
            "pin_coxa": 6, "pin_femur": 7, "pin_tibia": 8,
            "servo_zero_offset": 0.0,
            "joint_zero": {"coxa": 90.0, "femur": 0.0, "tibia": 0.0},
            "joint_range": {"coxa": (0, 180), "femur": (-45, 90), "tibia": (-90, 90)}
        }

        self.LR = {
            "name": "LR",
            "mount_x": -40, "mount_y": 40, "mount_angle": 0,
            "coxa_dir": 1, "femur_dir": 1, "tibia_dir": 1,
            "pin_coxa": 9, "pin_femur": 10, "pin_tibia": 11,
            "servo_zero_offset": 0.0,
            "joint_zero": {"coxa": 90.0, "femur": 5.0, "tibia": 0.0},
            "joint_range": {"coxa": (0, 180), "femur": (-45, 90), "tibia": (-90, 90)}
        }

        # Collections
        self.LEGS = [self.LF, self.RF, self.RR, self.LR]
        self.LEG_MAP = {leg["name"]: leg for leg in self.LEGS}
        self.PIN_LIST = [
            self.LF["pin_coxa"], self.LF["pin_femur"], self.LF["pin_tibia"],
            self.RF["pin_coxa"], self.RF["pin_femur"], self.RF["pin_tibia"],
            self.RR["pin_coxa"], self.RR["pin_femur"], self.RR["pin_tibia"],
            self.LR["pin_coxa"], self.LR["pin_femur"], self.LR["pin_tibia"],
        ]
