# crawler/arthropod_ik.py
import math
from crawler.hal_leg_hardware import COXA_LEN, FEMUR_LEN, TIBIA_LEN, MAX_REACH, FLOOR_DROP
from crawler.hal_leg_hardware import LEGS, LEG_MAP


class ArthropodIK:
    def __init__(self):
        self.C = COXA_LEN
        self.A = FEMUR_LEN
        self.B = TIBIA_LEN
        self.legs = LEGS
        self.leg_map = LEG_MAP
        self.max_reach = MAX_REACH
        self.floor_drop = FLOOR_DROP

    def coord2polar(self, leg, coord):
        # World → hip translation
        dx = coord[0] - leg.mount_x   # world forward
        dy = coord[1] - leg.mount_y   # world left

        # canonical coxa angle: atan2(left, forward)
        raw_angle_rad = math.atan2(dy, dx)   # radians, body-frame: forward=0°

        coxa_rad = raw_angle_rad
        theta_deg = math.degrees(coxa_rad)

        # compute horizontal reach after coxa
        px = math.sqrt(dx*dx + dy*dy) - self.C

        # Z baseline: full extension = Z=0
        user_z = coord[2]          # always positive
        pz = self.floor_drop - user_z

        # Law of Cosines for femur/tibia
        d = math.sqrt(px*px + pz*pz)
        d = max(abs(self.A - self.B) + 1.0, min(self.A + self.B - 1.0, d))

        # tibia
        cos_tibia = (self.A*self.A + self.B*self.B - d*d) / (2*self.A*self.B)
        cos_tibia = max(-1.0, min(1.0, cos_tibia))
        tibia_rad = math.pi - math.acos(cos_tibia)

        # femur
        angle_to_target = math.atan2(pz, px)
        cos_femur = (self.A*self.A + d*d - self.B*self.B) / (2*self.A*d)
        cos_femur = max(-1.0, min(1.0, cos_femur))
        femur_rad = angle_to_target - math.acos(cos_femur)

        # raw IK angles in degrees
        coxa_deg = math.degrees(coxa_rad)
        femur_deg = math.degrees(femur_rad)
        tibia_deg = math.degrees(tibia_rad)

        # rotate into leg frame if mount_angle is used
        theta_body_deg = coxa_deg - leg.mount_angle

        # per-leg servo_zero_offset must exist on LegHardware (default 0.0 if not set)
        servo_zero = getattr(leg, "servo_zero_offset", 0.0)

        # map IK angles into servo degrees using per-leg direction and hardware zero
        servo_coxa = leg.coxa_dir * (theta_body_deg - servo_zero) + leg.joint_zero["coxa"]
        servo_femur = leg.femur_dir * femur_deg + leg.joint_zero["femur"]
        servo_tibia = leg.tibia_dir * tibia_deg + leg.joint_zero["tibia"]

        # clamp to safe ranges
        servo_coxa = self.limit(leg.joint_range["coxa"][0], leg.joint_range["coxa"][1], servo_coxa)
        servo_femur = self.limit(leg.joint_range["femur"][0], leg.joint_range["femur"][1], servo_femur)
        servo_tibia = self.limit(leg.joint_range["tibia"][0], leg.joint_range["tibia"][1], servo_tibia)

        # debug trace to verify per-leg mapping
        print(f"[IK DEBUG] {leg.name} dx={dx:.1f} dy={dy:.1f} theta_deg={coxa_deg:.1f} "
            f"mount_angle={leg.mount_angle} servo_zero={servo_zero:.1f} "
            f"theta_body={theta_body_deg:.1f} coxa_dir={leg.coxa_dir} servo_coxa={servo_coxa:.1f}")

        # return servo-ready angles (degrees)
        return [servo_coxa, servo_femur, servo_tibia]

    def limit(self, min_val, max_val, x):
        if x > max_val:
            return max_val
        elif x < min_val:
            return min_val
        return x

    def limit_angle(self, leg, angles):
        coxa_deg, femur_deg, tibia_deg = angles
        coxa_min, coxa_max = leg.joint_range["coxa"]
        femur_min, femur_max = leg.joint_range["femur"]
        tibia_min, tibia_max = leg.joint_range["tibia"]

        safe_coxa  = max(coxa_min, min(coxa_max, coxa_deg))
        safe_femur = max(femur_min, min(femur_max, femur_deg))
        safe_tibia = max(tibia_min, min(tibia_max, tibia_deg))

        if safe_coxa != coxa_deg or safe_femur != femur_deg or safe_tibia != tibia_deg:
            print(f"[COLLISION BLOCK] Hard clamp applied on {leg.name} to protect hardware!")

        return [safe_coxa, safe_femur, safe_tibia]
