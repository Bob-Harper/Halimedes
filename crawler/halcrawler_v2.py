import math
from crawler.hal_leg_hardware import COXA_LEN, FEMUR_LEN, TIBIA_LEN, NEUTRAL
from crawler.hal_leg_hardware import LEGS, LEG_MAP
from crawler.robot import Robot

STANCE = {
    "A": {  # LF + RR wide, RF + LR straight
        "LF": {"x":  40, "y":  80, "z": -30},
        "LR": {"x": -40, "y":  80, "z": -30},
        "RF": {"x":  40, "y": -40, "z": -30},
        "RR": {"x": -40, "y": -80, "z": -30},
    },
    "B": {  # RF + LR wide, LF + RR straight
        "LF": {"x":  40, "y":  40, "z": -30},
        "LR": {"x": -40, "y":  80, "z": -30},
        "RF": {"x":  40, "y": -80, "z": -30},
        "RR": {"x": -40, "y": -40, "z": -30},
    }
}


class Halcrawler(Robot):
    def __init__(self,
                 pin_list,
                 name="hal",
                 init_angles=None,
                 init_order=None,
                 coxa_len=COXA_LEN,
                 femur_len=FEMUR_LEN,
                 tibia_len=TIBIA_LEN,
                 *args, **kwargs):

        # initialize Robot (servo hardware)
        super().__init__(pin_list=pin_list,
                         name=name,
                         init_angles=init_angles,
                         init_order=init_order,
                         **kwargs)

        self.C = coxa_len
        self.A = femur_len
        self.B = tibia_len
        self.legs = LEGS
        self.leg_map = LEG_MAP

    def coord2polar(self, leg, coord):
        dx = coord[0] - leg.mount_x
        dy = coord[1] - leg.mount_y

        BELLY_Z_OFFSET = 15
        dz = coord[2] - BELLY_Z_OFFSET

        theta = math.radians(leg.mount_angle)
        lx =  dx * math.cos(theta) + dy * math.sin(theta)
        ly = -dx * math.sin(theta) + dy * math.cos(theta)
        lz = dz

        coxa_rad = math.atan2(ly, lx)

        px = math.sqrt(lx**2 + ly**2) - self.C
        pz = lz

        d = math.sqrt(px**2 + pz**2)
        max_reach = self.A + self.B
        min_reach = abs(self.A - self.B)

        if d > max_reach:
            scale = (max_reach - 1.0) / d
            px *= scale
            pz *= scale
            d = max_reach - 1.0
        elif d < min_reach:
            scale = (min_reach + 1.0) / d
            px *= scale
            pz *= scale
            d = min_reach + 1.0

        cos_tibia = (self.A**2 + self.B**2 - d**2) / (2.0 * self.A * self.B)
        cos_tibia = max(-1.0, min(1.0, cos_tibia))
        tibia_internal = math.acos(cos_tibia)

        tibia_rad = math.pi - tibia_internal

        angle_to_target = math.atan2(pz, px)
        cos_femur = (self.A**2 + d**2 - self.B**2) / (2.0 * self.A * d)
        cos_femur = max(-1.0, min(1.0, cos_femur))
        femur_rad = angle_to_target + math.acos(cos_femur)

        return [math.degrees(coxa_rad), math.degrees(femur_rad), math.degrees(tibia_rad)]

    def polar2coord(self, leg, angles):
        coxa_deg, femur_deg, tibia_deg = angles

        # undo direction
        femur_deg /= leg.femur_dir
        tibia_deg /= leg.tibia_dir
        coxa_deg = coxa_deg / leg.coxa_dir


        # femur/tibia geometry
        L1 = math.sqrt(
            self.A*self.A + self.B*self.B
            - 2.0*self.A*self.B*math.cos((90.0 + femur_deg) * math.pi / 180.0)
        )
        angle = math.acos((self.A*self.A + L1*L1 - self.B*self.B) / (2.0*self.A*L1)) * 180.0 / math.pi
        angle = 90.0 - tibia_deg - angle
        L = L1 * math.cos(angle * math.pi / 180.0) + self.C

        # coxa yaw
        coxa_rad = coxa_deg * math.pi / 180.0
        x = L * math.cos(coxa_rad)
        y = L * math.sin(coxa_rad)
        z = L1 * math.sin(angle * math.pi / 180.0)

        # rotate back into world frame
        theta = math.radians(leg.mount_angle)

        # inverse rotation: local → world
        wx = lx * math.cos(theta) + ly * math.sin(theta)
        wy = -lx * math.sin(theta) + ly * math.cos(theta)
        wz = lz

        # add hip offset
        world_x = wx + leg.mount_x
        world_y = wy + leg.mount_y
        world_z = wz

        return [round(world_x,4), round(world_y,4), round(world_z,4)]

    def apply_calibration(self, leg, joint, logical_angle):
        zero = leg.joint_zero[joint]
        lo, hi = leg.joint_range[joint]
        angle = logical_angle + zero
        return max(lo, min(hi, angle))

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


    def set_leg_angles(self, leg_name, angles):
        leg = self.leg_map[leg_name]
        coxa, femur, tibia = angles

        # apply calibration before writing to servo_positions
        coxa  = self.apply_calibration(leg, "coxa", coxa)
        femur = self.apply_calibration(leg, "femur", femur)
        tibia = self.apply_calibration(leg, "tibia", tibia)

        print(f"{leg_name} SET:",
            f"coxa={coxa:.1f}",
            f"femur={femur:.1f}",
            f"tibia={tibia:.1f}")

        self.servo_positions[leg.pin_coxa]  = coxa
        self.servo_positions[leg.pin_femur] = femur
        self.servo_positions[leg.pin_tibia] = tibia

        self.servo_write_all(self.servo_positions)


    def move_leg_to(self, leg_name, target_coord):
        leg = self.leg_map[leg_name]

        # 1. Fetch the pure, flawless geometric angles from the math layer
        math_coxa, math_femur, math_tibia = self.coord2polar(leg, target_coord)

        # 2. MATCH THE PURE GEOMETRY RULES TO YOUR SERVO HARDWARE MAP
        # -------------------------------------------------------------
        # Coxa horizontal swing mapping
        servo_coxa = math_coxa * leg.coxa_dir

        # Femur: Pure math treats positive as UP. Your notes state 90 is DOWN.
        # We invert it so positive geometry commands pitch the servo UP.
        servo_femur = -math_femur * leg.femur_dir

        # Tibia: Pure geometry treats 0 as straight out, positive as bent downward.
        # Your notes state 90 is fully inward (bent), -90 is fully extended (straight).
        # We adjust the math baseline to match your 90-degree internal frame shift.
        adjusted_tibia = math_tibia - 90.0
        servo_tibia = adjusted_tibia * leg.tibia_dir

        # 3. Soft Limits Clamping (Intercepts crashes using your custom joint_ranges)
        coxa_min, coxa_max = leg.joint_range["coxa"]
        femur_min, femur_max = leg.joint_range["femur"]
        tibia_min, tibia_max = leg.joint_range["tibia"]

        final_coxa  = max(coxa_min, min(coxa_max, servo_coxa))
        final_femur = max(femur_min, min(femur_max, servo_femur))
        final_tibia = max(tibia_min, min(tibia_max, servo_tibia))

        # PRINT VERIFICATION: Shows you exactly what you typed vs what is leaving the engine
        print(f"\n[LIVE PIN DATA] Leg: {leg.name} | Input Coordinate: {target_coord} -> ENGINE OUTPUT: Coxa={final_coxa:.2f}°, Femur={final_femur:.2f}°, Tibia={final_tibia:.2f}°")

        # 4. Pass the leg name and your 3 final angles straight to your existing function
        # This allows set_leg_angles to handle its internal print and calibration safely!
        self.set_leg_angles(leg_name, [final_coxa, final_femur, final_tibia])
