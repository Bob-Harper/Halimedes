# crawler/halcrawler_v2.py

import math
from crawler.arthropod_ik import ArthropodIK
from crawler.robot import Robot
from crawler.hal_leg_hardware import HalLegs


class HalCrawler(Robot):
    def __init__(self,
                 pin_list,
                 init_angles=None,
                 init_order=None,
                 *args, **kwargs):

        super().__init__(pin_list=pin_list,
                         init_angles=init_angles,
                         init_order=init_order,
                         **kwargs)

        self.legs = HalLegs()
        self.leg_map = self.legs.LEG_MAP

        self.ik = ArthropodIK(
            self.legs.COXA_LEN,
            self.legs.FEMUR_LEN,
            self.legs.TIBIA_LEN,
            self.legs.FLOOR_DROP
        )

        self.C = self.legs.COXA_LEN
        self.A = self.legs.FEMUR_LEN
        self.B = self.legs.TIBIA_LEN

    def _clamp(self, x, lo, hi):
        return max(lo, min(hi, x))

    def set_leg_angles(self, leg_name, angles):
        leg = self.leg_map[leg_name]
        coxa_deg, femur_deg, tibia_deg = angles

        # per-leg servo zero offset
        servo_zero = leg["servo_zero_offset"]

        servo_coxa  = servo_zero + leg["coxa_dir"]  * coxa_deg + leg["joint_zero"]["coxa"]
        servo_femur = leg["femur_dir"] * femur_deg + leg["joint_zero"]["femur"]
        servo_tibia = leg["tibia_dir"] * tibia_deg + leg["joint_zero"]["tibia"]

        # clamp to safe ranges
        servo_coxa  = self._clamp(servo_coxa,  *leg["joint_range"]["coxa"])
        servo_femur = self._clamp(servo_femur, *leg["joint_range"]["femur"])
        servo_tibia = self._clamp(servo_tibia, *leg["joint_range"]["tibia"])

        # write to servos
        self.servo_list[leg["pin_coxa"]].angle  = servo_coxa
        self.servo_list[leg["pin_femur"]].angle = servo_femur
        self.servo_list[leg["pin_tibia"]].angle = servo_tibia

    def move_leg_to(self, leg_name, target_coord):
        leg = self.leg_map[leg_name]

        # raw IK angles
        coxa_deg, femur_deg, tibia_deg = self.ik.coord2polar(leg, target_coord)
        print(f"[MOVE_LEG] {leg_name} rawIK: C={coxa_deg:.1f} F={femur_deg:.1f} T={tibia_deg:.1f}")

        # clamp raw IK angles BEFORE mapping (safety)
        c_min, c_max = leg["joint_range"]["coxa"]
        f_min, f_max = leg["joint_range"]["femur"]
        t_min, t_max = leg["joint_range"]["tibia"]

        coxa_deg  = self._clamp(coxa_deg,  c_min, c_max)
        femur_deg = self._clamp(femur_deg, f_min, f_max)
        tibia_deg = self._clamp(tibia_deg, t_min, t_max)

        print(f"[LEG DATA] {leg_name}: {leg}")

        # send to servo mapping
        self.set_leg_angles(leg_name, [coxa_deg, femur_deg, tibia_deg])
