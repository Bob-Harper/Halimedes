from dataclasses import dataclass

@dataclass
class LegHardware:
    name: str

    # geometry
    mount_x: float
    mount_y: float
    mount_angle: float

    # directions
    coxa_dir: int
    femur_dir: int
    tibia_dir: int

    # servo pins
    pin_coxa: int
    pin_femur: int
    pin_tibia: int


# Physical hip locations (mm)
LF_X, LF_Y =  +40, +40
RF_X, RF_Y =  +40, -40
RR_X, RR_Y =  -40, -40
LR_X, LR_Y =  -40, +40

LF = LegHardware(
    name="LF",
    mount_x=40, mount_y=40, mount_angle=135,
    coxa_dir=-1, femur_dir=1, tibia_dir=1,
    pin_coxa=3, pin_femur=4, pin_tibia=5
)

RF = LegHardware(
    name="RF",
    mount_x=40, mount_y=-40, mount_angle=45,
    coxa_dir=1, femur_dir=1, tibia_dir=1,
    pin_coxa=9, pin_femur=10, pin_tibia=11
)

RR = LegHardware(
    name="RR",
    mount_x=-40, mount_y=-40, mount_angle=-45,
    coxa_dir=-1, femur_dir=1, tibia_dir=1,
    pin_coxa=6, pin_femur=7, pin_tibia=8
)

LR = LegHardware(
    name="LR",
    mount_x=-40, mount_y=40, mount_angle=-135,
    coxa_dir=1, femur_dir=1, tibia_dir=1,
    pin_coxa=0, pin_femur=1, pin_tibia=2
)


LEGS = [LF, RF, RR, LR]
LEG_MAP = { leg.name: leg for leg in LEGS }
PIN_LIST = [5,4,3, 11,10,9, 8,7,6, 2,1,0]

# -----------------------------
# Linkage lengths (millimeters)
# -----------------------------
COXA_LEN  = 33
FEMUR_LEN = 48
TIBIA_LEN = 80

# Neutral Stance
LF_NEUTRAL = ( +110, +80, -20 )
RF_NEUTRAL = ( +110, -80, -20 )
RR_NEUTRAL = ( -110, -80, -20 )
LR_NEUTRAL = ( -110, +80, -20 )

NEUTRAL = {
    "LF": LF_NEUTRAL,
    "RF": RF_NEUTRAL,
    "RR": RR_NEUTRAL,
    "LR": LR_NEUTRAL
}
