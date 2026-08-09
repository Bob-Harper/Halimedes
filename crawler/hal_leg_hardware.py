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

    joint_zero = {"coxa": 0.0, "femur": 0.0, "tibia": 0.0}
    joint_range = {
        "coxa": (-45.0, 45.0),
        "femur": (-75.0, 90.0),
        "tibia": (-90.0, 90.0),
    }

# Physical hip locations (mm)
LF_X, LF_Y =  +40, +40
RF_X, RF_Y =  +40, -40
RR_X, RR_Y =  -40, -40
LR_X, LR_Y =  -40, +40

LF = LegHardware(
    name="LF",
    mount_x=40, mount_y=40,
    mount_angle=45,             # FIXED: Points forward-left diagonal
    coxa_dir=1,                  # Positive swings outward (left)
    femur_dir=-1,                # Positive pitches down
    tibia_dir=-1,                 # FIXED: Left side tibia behavior is inverted
    pin_coxa=5, pin_femur=4, pin_tibia=3
)
LF.joint_zero = {"coxa": 7.0, "femur": -15.0, "tibia": 0.0}
LF.joint_range = {"coxa": (-60, 60), "femur": (-90, 90), "tibia": (-90, 90)}

RF = LegHardware(
    name="RF",
    mount_x=40, mount_y=-40,
    mount_angle=-45,              # CONFIRMED
    coxa_dir=1,                  # Positive swings outward (right)
    femur_dir=-1,                # Positive pitches down
    tibia_dir=-1,                # Confirmed
    pin_coxa=11, pin_femur=10, pin_tibia=9
)
RF.joint_zero = {"coxa": 0.0, "femur": 0.0, "tibia": 0.0}
RF.joint_range = {"coxa": (-60, 60), "femur": (-90, 90), "tibia": (-90, 90)}

RR = LegHardware(
    name="RR",
    mount_x=-40, mount_y=-40,
    mount_angle=-135,             # FIXED: Points back-right diagonal (-45)
    coxa_dir=1,
    femur_dir=-1,
    tibia_dir=-1,
    pin_coxa=8, pin_femur=7, pin_tibia=6
)
RR.joint_zero = {"coxa": 0.0, "femur": -0.0, "tibia": 0.0}
RR.joint_range = {"coxa": (-60, 60), "femur": (-90, 90), "tibia": (-90, 90)}

LR = LegHardware(
    name="LR",
    mount_x=-40, mount_y=40,
    mount_angle=135,            # FIXED: Points back-left diagonal (-135)
    coxa_dir=1,
    femur_dir=-1,
    tibia_dir=-1,                 # FIXED: Left side tibia inversion
    pin_coxa=2, pin_femur=1, pin_tibia=0
)
LR.joint_zero = {"coxa": 7.0, "femur": 10.0, "tibia": 0.0}
LR.joint_range = {"coxa": (-60, 60), "femur": (-90, 90), "tibia": (-90, 90)}

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


"""

  -------- PiCrawler Servo Layout ---------
	Arrows indicate which side of the servo block the pivot point is on

	            Front
       .......          .......
    <=|  LF   |-U----U-|  RF   |=>
       ``````` |      | ```````
  L    ....... |      | .......    R
    <=|  LR   |--------|  RR   |=>
       ```````          ```````
	             BACK

RF
    pin_coxa=11, 45 straight forward, -45 straight right,
    pin_femur=10, # unknown, servo awaiting replacement
    pin_tibia=9, 90 fully inward, -90 fully extended

RR
    pin_coxa=8, -45 straight back,  45 straight right,
    pin_femur=7,-75 straight up, 90 (30 degrees downward)
    pin_tibia=6, 90 fully inward, -90 fully extended

LF
    pin_coxa=5, 55 straight left, -40 straight forward
    pin_femur=4,-75 straight up, 90 (45 degrees downward)
    pin_tibia=3, 90 fully inward, -90 fully extended

LR
    pin_coxa=2, -45 straight left, 60 straight back.
    pin_femur=1, -45 straight up, 90 (45 degrees downward)
    pin_tibia=0, 90 fully inward, -90 fully extended


"""