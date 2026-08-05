# crawler/hal_geometry.py

from dataclasses import dataclass

# -----------------------------
# Linkage lengths (millimeters)
# -----------------------------
COXA_LEN  = 33
FEMUR_LEN = 48
TIBIA_LEN = 80

@dataclass
class LegDefinition:
    name: str
    mount_x: float
    mount_y: float
    mount_angle: float
    coxa_dir: int
    femur_dir: int
    tibia_dir: int

# -----------------------------------------
# Body coordinate system (center = Raspberry Pi)
# +X = forward (eyes)
# +Y = left
# -----------------------------------------

# Working hip locations (mm)
LF_X, LF_Y =  +40, +40
RF_X, RF_Y =  +40, -40
RR_X, RR_Y =  -40, -40
LR_X, LR_Y =  -40, +40

# -----------------------------------------
# Leg definitions (physical reality only)
# -----------------------------------------

LF = LegDefinition(
    name="LF",
    mount_x=LF_X,
    mount_y=LF_Y,
    mount_angle=135,
    coxa_dir=-1,
    femur_dir=1,
    tibia_dir=1
)

RF = LegDefinition(
    name="RF",
    mount_x=RF_X,
    mount_y=RF_Y,
    mount_angle=45,
    coxa_dir=1,
    femur_dir=1,
    tibia_dir=1
)

RR = LegDefinition(
    name="RR",
    mount_x=RR_X,
    mount_y=RR_Y,
    mount_angle=-45,
    coxa_dir=-1,
    femur_dir=1,
    tibia_dir=1
)

LR = LegDefinition(
    name="LR",
    mount_x=LR_X,
    mount_y=LR_Y,
    mount_angle=-135,
    coxa_dir=1,
    femur_dir=1,
    tibia_dir=1
)

# Export list for iteration
LEGS = [LF, RF, RR, LR]

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

SERVOS = [LF, RF, RR, LR]
PIN_LIST = [5,4,3, 11,10,9, 8,7,6, 2,1,0]