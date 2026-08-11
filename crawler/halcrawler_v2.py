# crawler/halcrawler_v2.py

import math
from crawler.arthropod_ik import ArthropodIK
from crawler.robot import Robot


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

        self.ik = ArthropodIK()   # FIXED

    def set_leg_angles(self, leg_name, angles):
        leg = self.ik.leg_map[leg_name]
        coxa, femur, tibia = angles

        # apply joint_zero offsets
        coxa  = leg.joint_zero["coxa"]  + coxa
        femur = leg.joint_zero["femur"] + femur
        tibia = leg.joint_zero["tibia"] + tibia

        self.servo_positions[leg.pin_coxa]  = coxa
        self.servo_positions[leg.pin_femur] = femur
        self.servo_positions[leg.pin_tibia] = tibia

        self.servo_write_all(self.servo_positions)

    def move_leg_to(self, leg_name, target_coord):
        leg = self.ik.leg_map[leg_name]

        # FIXED: call IK correctly
        math_coxa, math_femur, math_tibia = self.ik.coord2polar(leg, target_coord)

        # apply directions
        servo_coxa  = math_coxa  * leg.coxa_dir
        servo_femur = math_femur * leg.femur_dir
        servo_tibia = math_tibia * leg.tibia_dir

        print(f"[SERVO CMD] {leg.name} servo_coxa={servo_coxa:.1f} servo_femur={servo_femur:.1f} servo_tibia={servo_tibia:.1f}")
        print("servo_positions before write:", ", ".join(f"{v:.1f}" if v is not None else "None" for v in self.servo_positions))

        # clamp
        coxa_min, coxa_max = leg.joint_range["coxa"]
        femur_min, femur_max = leg.joint_range["femur"]
        tibia_min, tibia_max = leg.joint_range["tibia"]



        final_coxa  = max(coxa_min, min(coxa_max, servo_coxa))
        final_femur = max(femur_min, min(femur_max, servo_femur))
        final_tibia = max(tibia_min, min(tibia_max, servo_tibia))

        # after computing servo_coxa, adding joint_zero, and clamping to final_coxa
        print(f"[FINAL CMD] {leg.name} math_coxa={math_coxa:.1f} servo_coxa(before zero)={(math_coxa*leg.coxa_dir):.1f} servo_coxa(with zero)={(math_coxa*leg.coxa_dir + leg.joint_zero['coxa']):.1f} final_coxa={final_coxa:.1f}")
        self.set_leg_angles(leg_name, [final_coxa, final_femur, final_tibia])
