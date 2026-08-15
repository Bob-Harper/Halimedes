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
        )

        self.C = self.legs.COXA_LEN
        self.A = self.legs.FEMUR_LEN
        self.B = self.legs.TIBIA_LEN

    def _clamp(self, x, lo, hi):
        return max(lo, min(hi, x))

    def set_leg_angles(self, leg_name, angles):
        leg = self.leg_map[leg_name]
        coxa, femur, tibia = angles

        if hasattr(leg, "__dict__") and not isinstance(leg, dict):
            leg = vars(leg)

        # 1. FIXED PHYSICAL HIP SPLIT (All 4 legs swing FORWARD together)
        # Because the left and right servo banks are physical mirror images,
        # we adjust the math symbols so a forward step drives all hips forward.
        if leg_name in ["LF", "LR"]:
            servo_coxa = 90.0 + coxa   # Left side: Positive math swings hip FORWARD
        else:
            servo_coxa = 90.0 - coxa   # Right side: Positive math swings hip FORWARD

        # 2. FIXED VERTICAL LINKAGES (No more meerkat stance)
        # Femur tracks smoothly down to its 45-degree resting incline
        servo_femur = 45.0 - femur

        # Tibia Inversion Fix: By subtracting tibia from 90.0 instead of tibia - 90.0,
        # a opening triangle angle mathematically forces the physical servo horn
        # to rotate OUTWARD away from the chassis, extending the foot down to the grid.
        servo_tibia = 90.0 - tibia

        c_min, c_max = leg["joint_range"]["coxa"]
        f_min, f_max = leg["joint_range"]["femur"]
        t_min, t_max = leg["joint_range"]["tibia"]

        # Universal safety clamps
        final_coxa  = max(c_min, min(c_max, servo_coxa))
        final_femur = max(f_min, min(f_max, servo_femur))
        final_tibia = max(t_min, min(t_max, servo_tibia))

        # Push clean, synchronized angles straight to your physical pin indices
        self.servo_list[leg["pin_coxa"]].angle  = final_coxa
        self.servo_list[leg["pin_femur"]].angle = final_femur
        self.servo_list[leg["pin_tibia"]].angle = final_tibia

    def move_leg_to(self, leg_name, target_coord):
        leg = self.leg_map[leg_name]
        x, y, z = target_coord

        # Calculate pure displacement vectors from the leg's unique physical mount point
        dx = x - leg["mount_x"]
        dy = y - leg["mount_y"]
        dz = z  # Raw target vertical distance from the shoulder axis line

        # Call the pure solver to get the abstract triangle degrees
        coxa_deg, femur_deg, tibia_deg = self.ik.solve_leg_triangle(dx, dy, dz)

        print(f"[MOVE_LEG] {leg_name} Raw Triangle: C={coxa_deg:.1f}° F={femur_deg:.1f}° T={tibia_deg:.1f}°")

        # Send the clean geometric angles straight down to your execution layer
        self.set_leg_angles(leg_name, [coxa_deg, femur_deg, tibia_deg])

