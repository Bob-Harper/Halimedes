# crawler/arthropod_ik.py
import math
import math

class ArthropodIK:
    def __init__(self, coxa_len, femur_len, tibia_len, floor_drop):
        self.C = coxa_len
        self.A = femur_len
        self.B = tibia_len
        self.floor_drop = floor_drop

    def coord2polar(self, leg, coord):
        dx = coord[0] - leg["mount_x"]
        dy = coord[1] - leg["mount_y"]
        rot = math.radians(leg["mount_angle"])
        dx2 = dx*math.cos(rot) + dy*math.sin(rot)
        dy2 = -dx*math.sin(rot) + dy*math.cos(rot)

        coxa_rad = math.atan2(dy, dx)
        # use mount_angle to rotate the leg’s local frame
        coxa_deg = math.degrees(coxa_rad) - leg["mount_angle"]
        # normalize to -180..+180
        # coxa_deg = ((coxa_deg + 180.0) % 360.0) - 180.0
        px = math.sqrt(dx2*dx2 + dy2*dy2) - self.C

        user_z = coord[2]
        pz = self.floor_drop - user_z

        d = math.sqrt(px*px + pz*pz)
        d = max(abs(self.A - self.B) + 1.0, min(self.A + self.B - 1.0, d))

        cos_tibia = (self.A*self.A + self.B*self.B - d*d) / (2*self.A*self.B)
        tibia_rad = math.pi - math.acos(max(-1.0, min(1.0, cos_tibia)))

        angle_to_target = math.atan2(pz, px)
        cos_femur = (self.A*self.A + d*d - self.B*self.B) / (2*self.A*d)
        femur_rad = angle_to_target - math.acos(max(-1.0, min(1.0, cos_femur)))

        return [
            coxa_deg,                      # ← use this instead of math.degrees(coxa_rad)
            math.degrees(femur_rad),
            math.degrees(tibia_rad)
        ]
