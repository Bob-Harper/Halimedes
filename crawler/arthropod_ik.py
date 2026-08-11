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
        dx = coord[0] - leg.mount_x
        dy = coord[1] - leg.mount_y

        # lx = dy
        # ly = dx
        # PER‑LEG ROTATION
        if leg.name == "LF":
            lx = dy
            ly = dx

        elif leg.name == "RF":
            lx = -dy
            ly = -dx

        elif leg.name == "LR":
            lx = dy
            ly = dx

        elif leg.name == "RR":
            lx = -dy
            ly = -dx

        # Z baseline: full extension = Z=0
        user_z = coord[2]          # always positive
        pz = self.floor_drop - user_z

        # Coxa angle (arthropod lateral hinge)
        coxa_rad = math.atan2(lx, ly)

        # Project into vertical plane
        px = math.sqrt(lx*lx + ly*ly) - self.C

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

        # Output degrees (raw math only)
        return [
            math.degrees(coxa_rad),
            math.degrees(femur_rad),
            math.degrees(tibia_rad)
        ]

    def polar2coord(self, leg, angles):
        # Will not work with new math, fix before trying to call this if it is even needed.
        coxa_deg, femur_deg, tibia_deg = angles
        femur_deg /= leg.femur_dir
        tibia_deg /= leg.tibia_dir
        coxa_deg = coxa_deg / leg.coxa_dir
        return [round(world_x,4), round(world_y,4), round(world_z,4)]

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