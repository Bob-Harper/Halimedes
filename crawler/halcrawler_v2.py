import math
from crawler.hal_leg_hardware import COXA_LEN, FEMUR_LEN, TIBIA_LEN, NEUTRAL
from crawler.hal_leg_hardware import LEGS, LEG_MAP
from crawler.robot import Robot


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
        # world → leg-local
        dx = coord[0] - leg.mount_x
        dy = coord[1] - leg.mount_y
        dz = coord[2]

        # rotate into leg frame
        theta = math.radians(leg.mount_angle)
        lx = dx * math.cos(theta) + dy * math.sin(theta)
        ly = -dx * math.sin(theta) + dy * math.cos(theta)
        lz = dz

        # coxa yaw
        raw_coxa = math.atan2(ly, lx)
        coxa_rad = raw_coxa

        # femur/tibia plane
        px = math.sqrt(lx*lx + ly*ly) - self.C
        pz = lz
        d = math.sqrt(px*px + pz*pz)
        if d < 1.0:
            d = 1.0

        # tibia
        cos_tibia = (self.A*self.A + self.B*self.B - d*d) / (2.0 * self.A * self.B)
        cos_tibia = max(-1.0, min(1.0, cos_tibia))
        tibia_rad = math.acos(cos_tibia)

        # femur
        angle_to_target = math.atan2(pz, px)
        cos_femur = (self.A*self.A + d*d - self.B*self.B) / (2.0 * self.A * d)
        cos_femur = max(-1.0, min(1.0, cos_femur))
        femur_rad = angle_to_target + math.acos(cos_femur)

        # to degrees
        coxa_deg  = math.degrees(coxa_rad)  * leg.coxa_dir
        femur_deg = math.degrees(femur_rad) * leg.femur_dir
        tibia_deg = math.degrees(tibia_rad) * leg.tibia_dir

        return [round(coxa_deg, 4), round(femur_deg, 4), round(tibia_deg, 4)]



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
        wx =  x * math.cos(theta) - y * math.sin(theta)
        wy =  x * math.sin(theta) + y * math.cos(theta)
        wz =  z

        # translate back to world
        wx += leg.mount_x
        wy += leg.mount_y

        return [round(wx,4), round(wy,4), round(wz,4)]

    def limit(self, min_val, max_val, x):
        if x > max_val:
            return max_val
        elif x < min_val:
            return min_val
        return x

    def limit_angle(self, angles):
        coxa_deg, femur_deg, tibia_deg = angles

        t = self.limit(-90, 90, coxa_deg)
        if t != coxa_deg:
            coxa_deg = t

        t = self.limit(-90, 90, femur_deg)
        if t != femur_deg:
            femur_deg = t

        t = self.limit(-90, 90, tibia_deg)
        if t != tibia_deg:
            tibia_deg = t

        return [coxa_deg, femur_deg, tibia_deg]

    def set_leg_angles(self, leg_name, angles):
        leg = self.leg_map[leg_name]
        coxa, femur, tibia = angles
        print(f"{leg_name} SET:",
            f"coxa={coxa:.1f}",
            f"femur={femur:.1f}",
            f"tibia={tibia:.1f}")
        self.servo_positions[leg.pin_coxa]  = coxa
        self.servo_positions[leg.pin_femur] = femur
        self.servo_positions[leg.pin_tibia] = tibia

        self.servo_write_all(self.servo_positions)


    def move_leg_to(self, leg_name, coord):
        leg = self.leg_map[leg_name]
        angles = self.coord2polar(leg, coord)
        limited = self.limit_angle(angles)
        self.set_leg_angles(leg_name, limited)



    def assume_neutral(self):
        for leg_name, coord in NEUTRAL.items():
            self.move_leg_to(leg_name, coord)

    def move_leg_smooth(self, leg_name, target, steps=20):
        leg = self.leg_map[leg_name]
        current = self.polar2coord(leg, (
            self.servo_positions[leg.pin_coxa],
            self.servo_positions[leg.pin_femur],
            self.servo_positions[leg.pin_tibia]
        ))

        for i in range(steps):
            t = i / (steps - 1)
            x = current[0] + (target[0] - current[0]) * t
            y = current[1] + (target[1] - current[1]) * t
            z = current[2] + (target[2] - current[2]) * t
            self.move_leg_to(leg_name, (x, y, z))
