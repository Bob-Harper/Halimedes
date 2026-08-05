import math
from crawler.hal_geometry import COXA_LEN, FEMUR_LEN, TIBIA_LEN, NEUTRAL
from crawler.hal_leg_config import LEGS
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
        self.legs = { leg.name: leg for leg in LEGS }


    def coord2polar(self, leg, coord):
        print("coord2polar USING:", leg.name, leg.mount_angle)

        # world → leg-local
        dx = coord[0] - leg.mount_x
        dy = coord[1] - leg.mount_y
        dz = coord[2]

        theta = -math.radians(leg.mount_angle)
        lx = dx * math.cos(theta) + dy * math.sin(theta)
        ly = -dx * math.sin(theta) + dy * math.cos(theta)
        lz = dz

        # coxa yaw
        coxa_rad = math.atan2(ly, lx)

        # femur/tibia plane
        px = lx - self.C
        pz = lz
        d = math.sqrt(px*px + pz*pz)
        if d < 1.0:
            d = 1.0

        # tibia via law of cosines
        cos_tibia = (self.A*self.A + self.B*self.B - d*d) / (2.0 * self.A * self.B)
        cos_tibia = max(-1.0, min(1.0, cos_tibia))
        tibia_rad = math.acos(cos_tibia)

        # femur
        angle_to_target = math.atan2(pz, px)
        cos_femur = (self.A*self.A + d*d - self.B*self.B) / (2.0 * self.A * d)
        cos_femur = max(-1.0, min(1.0, cos_femur))
        femur_rad = angle_to_target + math.acos(cos_femur)

        # to degrees
        coxa_deg  = math.degrees(coxa_rad)
        femur_deg = math.degrees(femur_rad)
        tibia_deg = math.degrees(tibia_rad)

        # apply directions
        coxa_deg  *= leg.coxa_dir
        femur_deg *= leg.femur_dir
        tibia_deg *= leg.tibia_dir

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
        leg = self.legs[leg_name]
        coxa, femur, tibia = angles

        # Write into the correct servo slots
        self.servo_positions[leg.coxa_pin]  = coxa
        self.servo_positions[leg.femur_pin] = femur
        self.servo_positions[leg.tibia_pin] = tibia

        # Push to hardware
        self.servo_write_all(self.servo_positions)

    def move_leg_to(self, leg_name, coord):
        leg = self.legs[leg_name]
        angles = self.coord2polar(leg, coord)
        limited = self.limit_angle(angles)
        self.set_leg_angles(leg_name, limited)


    def assume_neutral(self):
        for leg_name, coord in NEUTRAL.items():
            self.move_leg_to(leg_name, coord)

    def move_leg_smooth(self, leg_name, target, steps=20):
        leg = self.legs[leg_name]
        current = self.polar2coord(leg, (
            self.servo_positions[leg.coxa_pin],
            self.servo_positions[leg.femur_pin],
            self.servo_positions[leg.tibia_pin]
        ))

        for i in range(steps):
            t = i / (steps - 1)
            x = current[0] + (target[0] - current[0]) * t
            y = current[1] + (target[1] - current[1]) * t
            z = current[2] + (target[2] - current[2]) * t
            self.move_leg_to(leg_name, (x, y, z))
