# crawler/halcrawler_v2.py

import math
from crawler.arthropod_ik import ArthropodIK
from crawler.robot import Robot
from crawler.hal_leg_hardware import LEG_MAP, COXA_LEN, FEMUR_LEN, TIBIA_LEN

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

        self.ik = ArthropodIK()

        # BIND THE DICTIONARY SO MOVE_LEG_TO CAN ACCESS IT
        self.leg_map = LEG_MAP

        # Cache the physical linkage dimensions for easy access if needed
        self.C = kwargs.get('coxa_len', COXA_LEN)
        self.A = kwargs.get('femur_len', FEMUR_LEN)
        self.B = kwargs.get('tibia_len', TIBIA_LEN)

    def set_leg_angles(self, leg_name, angles):
        leg = self.leg_map[leg_name]
        coxa_deg, femur_deg, tibia_deg = angles

        # Map IK -> servo frame here (per-leg)
        servo_zero = getattr(leg, "servo_zero_offset", 0.0)

        servo_coxa = leg.coxa_dir * (coxa_deg - servo_zero) + leg.joint_zero["coxa"]
        servo_femur = leg.femur_dir * femur_deg + leg.joint_zero["femur"]
        servo_tibia = leg.tibia_dir * tibia_deg + leg.joint_zero["tibia"]

        # clamp to safe ranges
        servo_coxa = max(leg.joint_range["coxa"][0], min(leg.joint_range["coxa"][1], servo_coxa))
        servo_femur = max(leg.joint_range["femur"][0], min(leg.joint_range["femur"][1], servo_femur))
        servo_tibia = max(leg.joint_range["tibia"][0], min(leg.joint_range["tibia"][1], servo_tibia))

        # Write to servos
        self.servo_list[leg.pin_coxa].angle  = servo_coxa
        self.servo_list[leg.pin_femur].angle = servo_femur
        self.servo_list[leg.pin_tibia].angle = servo_tibia

    def move_leg_to(self, leg_name, target_coord):
        leg = self.leg_map[leg_name]

        # Calculate raw angles from your engine
        math_coxa, math_femur, math_tibia = self.ik.coord2polar(leg, target_coord)
        print(f"[MOVE_LEG] {leg.name} rawIK: C={math_coxa:.1f}° F={math_femur:.1f}° T={math_tibia:.1f}°")

        # Pure 1-to-1 matching to let your math engine drive the 180-degree hardware scale
        # Inverting the coxa tracks with the motor's counterclockwise physical rotation profile
        servo_coxa  = math_coxa # * 5.36
        servo_femur = math_femur
        servo_tibia = math_tibia

        # Unpack the updated float bounds to protect the physical limbs
        c_min, c_max = leg.joint_range["coxa"]
        f_min, f_max = leg.joint_range["femur"]
        t_min, t_max = leg.joint_range["tibia"]

        # Safety clamps
        final_coxa  = max(c_min, min(c_max, servo_coxa))
        final_femur = max(f_min, min(f_max, servo_femur))
        final_tibia = max(t_min, min(t_max, servo_tibia))
        print(f"[MOVE_LEG] {leg.name} final (to servo): C={final_coxa:.1f}° F={final_femur:.1f}° T={final_tibia:.1f}°")

        self.set_leg_angles(leg_name, [final_coxa, final_femur, final_tibia])
