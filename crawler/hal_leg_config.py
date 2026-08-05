class Leg:
    def __init__(self,
                 name,
                 mount_x, mount_y, mount_angle,
                 coxa_dir, femur_dir, tibia_dir,
                 pin_coxa, pin_femur, pin_tibia):
        self.name = name

        # geometry
        self.mount_x = mount_x
        self.mount_y = mount_y
        self.mount_angle = mount_angle

        # directions
        self.coxa_dir = coxa_dir
        self.femur_dir = femur_dir
        self.tibia_dir = tibia_dir

        # servo pins
        self.coxa_pin = pin_coxa
        self.femur_pin = pin_femur
        self.tibia_pin = pin_tibia


LF = Leg(
    name="LF",
    mount_x=40, mount_y=40, mount_angle=45,
    coxa_dir=-1, femur_dir=1, tibia_dir=1,
    pin_coxa=5, pin_femur=4, pin_tibia=3
)

RF = Leg(
    name="RF",
    mount_x=40, mount_y=-40, mount_angle=-45,
    coxa_dir=1, femur_dir=1, tibia_dir=1,
    pin_coxa=11, pin_femur=10, pin_tibia=9
)

RR = Leg(
    name="RR",
    mount_x=-40, mount_y=-40, mount_angle=-135,
    coxa_dir=-1, femur_dir=1, tibia_dir=1,
    pin_coxa=8, pin_femur=7, pin_tibia=6
)

LR = Leg(
    name="LR",
    mount_x=-40, mount_y=40, mount_angle=135,
    coxa_dir=1, femur_dir=1, tibia_dir=1,
    pin_coxa=2, pin_femur=1, pin_tibia=0
)

LEGS = [LF, RF, RR, LR]

