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

        # apply direction and zero (assumes math_coxa/math_femur/math_tibia already computed)
        servo_coxa  = math_coxa  * leg.coxa_dir
        servo_femur = math_femur * leg.femur_dir
        servo_tibia = math_tibia * leg.tibia_dir

        # apply per-leg zero offsets (use 0.0 if not set)
        servo_coxa  += leg.joint_zero.get("coxa",  0.0)
        servo_femur += leg.joint_zero.get("femur", 0.0)
        servo_tibia += leg.joint_zero.get("tibia", 0.0)

        # get mechanical ranges from leg.joint_range if available, else use safe defaults
        coxa_min,  coxa_max  = leg.joint_range.get("coxa",  (-90.0, 90.0))
        femur_min, femur_max = leg.joint_range.get("femur", (-90.0, 90.0))
        tibia_min, tibia_max = leg.joint_range.get("tibia", (-90.0, 90.0))

        # clamp to ranges
        final_coxa  = max(coxa_min,  min(coxa_max,  servo_coxa))
        final_femur = max(femur_min, min(femur_max, servo_femur))
        final_tibia = max(tibia_min, min(tibia_max, servo_tibia))

        # definitive debug line showing the full transform chain
        print(f"[FINAL CMD] {leg.name} math_coxa={math_coxa:.1f} servo_coxa(before zero)={(math_coxa*leg.coxa_dir):.1f} servo_coxa(with zero)={servo_coxa:.1f} final_coxa={final_coxa:.1f}")

        # --- write final angles into servo array using per-leg mapping ---
        new_positions = list(self.servo_positions)

        m = getattr(leg, "servo_index_map", None)
        if m:
            if "coxa" in m:  new_positions[m["coxa"]]  = final_coxa
            if "femur" in m: new_positions[m["femur"]] = final_femur
            if "tibia" in m: new_positions[m["tibia"]] = final_tibia
        else:
            print(f"[ERROR] no servo_index_map for leg {leg.name}; not writing servo values")
            return

        # debug: show exactly what we will send
        rounded = [round(v, 1) if v is not None else None for v in new_positions]
        print(f"[WRITE DEBUG] leg={leg.name} map={m} new_positions={rounded}")

        # send to hardware
        self.servo_write_all(rounded)
        # --- end replacement ---
        # --- end replacement ---


