# crawler/arthropod_ik.py
import math

class ArthropodIK:
    def __init__(self, coxa_len=33, femur_len=48, tibia_len=80, *args, **kwargs):
        self.C = coxa_len
        self.A = femur_len
        self.B = tibia_len

    def solve_leg_triangle(self, dx, dy, dz):
        """Solves a pure geometric triangle for an upward-slanted limb configuration."""
        # 1. Pure horizontal coxa angle relative to the side axis (abs(dy))
        coxa_rad = math.atan2(dy, dx)
        # print(f"DEBUG dx={dx:.2f} dy={dy:.2f} coxa_rad={coxa_rad:.4f} coxa_deg={math.degrees(coxa_rad):.2f}")
        # 2. Horizontal extension distance past the hip joint
        px = math.sqrt(dx*dx + dy*dy) - self.C

        # 3. For an upward-slanted link setup where the foot is at the baseplate,
        # pz represents the true vertical depth coordinate below the hip pivot.
        pz = dz

        # 4. Straight-line hypotenuse distance from hip core to foot tip
        d = math.sqrt(px*px + pz*pz)

        # Safety constraint to prevent math domain violations
        max_reach = self.A + self.B
        min_reach = abs(self.A - self.B)
        d = max(min_reach + 0.1, min(max_reach - 0.1, d))

        # 5. Law of Cosines for the bone links
        cos_tibia = (self.A*self.A + self.B*self.B - d*d) / (2.0 * self.A * self.B)
        cos_tibia = max(-1.0, min(1.0, cos_tibia))
        tibia_rad = math.pi - math.acos(cos_tibia)

        # To resolve a triangle that slants upward first, the femur pitch angle
        # subtracts the internal cosine variation from the baseline tracking slant!
        angle_to_target = math.atan2(pz, px)

        cos_femur = (self.A*self.A + d*d - self.B*self.B) / (2.0 * self.A * d)
        cos_femur = max(-1.0, min(1.0, cos_femur))
        femur_rad = angle_to_target - math.acos(cos_femur)

        # Return pure, raw, unaltered mathematical degrees relative to the horizon
        return [
            math.degrees(coxa_rad),
            math.degrees(femur_rad),
            math.degrees(tibia_rad)
        ]