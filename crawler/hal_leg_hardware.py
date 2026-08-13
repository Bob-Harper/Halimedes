# crawler/hal_leg_hardware.py
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
        "coxa": (-90.0, 90.0),
        "femur": (-45.0, 90.0),
        "tibia": (-90.0, 90.0),
    }

    servo_zero_offset: float = 0.0   # degrees: converts body-forward zero → servo zero

# Physical hip locations (mm)
LF_X, LF_Y =  +40, +40
RF_X, RF_Y =  +40, -40
RR_X, RR_Y =  -40, -40
LR_X, LR_Y =  -40, +40

LF = LegHardware(
    name="LF",
    mount_x=40, mount_y=40, mount_angle=0,
    coxa_dir=1, femur_dir=1, tibia_dir=1,
    pin_coxa=0, pin_femur=1, pin_tibia=2
)
LF.servo_index_map = {"coxa": 0, "femur":1, "tibia": 2}
LF.joint_zero = {"coxa": 0.0, "femur": 0.0, "tibia": 0.0}
LF.joint_range = {"coxa": (-90, 90), "femur": (-45, 90), "tibia": (-90, 90)}

RF = LegHardware(
    name="RF",
    mount_x=40, mount_y=-40, mount_angle=0,
    coxa_dir=-1, femur_dir=1, tibia_dir=1,
    pin_coxa=3, pin_femur=4, pin_tibia=5
)
RF.servo_index_map = {"coxa": 3, "femur": 4, "tibia": 5}
RF.joint_zero = {"coxa": 0.0, "femur": 0.0, "tibia": 0.0}
RF.joint_range = {"coxa": (-90, 90), "femur": (-45, 90), "tibia": (-90, 90)}

RR = LegHardware(
    name="RR",
    mount_x=-40, mount_y=-40, mount_angle=0,
    coxa_dir=-1, femur_dir=1, tibia_dir=1,
    pin_coxa=6, pin_femur=7, pin_tibia=8
)
RR.servo_index_map = {"coxa": 6, "femur": 7, "tibia": 8}
RR.joint_zero = {"coxa": 0.0, "femur": 0.0, "tibia": 0.0}
RR.joint_range = {"coxa": (-90, 90), "femur": (-45, 90), "tibia": (-90, 90)}

LR = LegHardware(
    name="LR",
    mount_x=-40, mount_y=40, mount_angle=0,
    coxa_dir=1, femur_dir=1, tibia_dir=1,
    pin_coxa=9, pin_femur=10, pin_tibia=11
)
LR.servo_index_map = {"coxa": 9, "femur": 10, "tibia": 11}
LR.joint_zero = {"coxa": 0.0, "femur": 0.0, "tibia": 0.0}
LR.joint_range = {"coxa": (-90, 90), "femur": (-45, 90), "tibia": (-90, 90)}


LEGS = [LF, RF, RR, LR]
LEG_MAP = { leg.name: leg for leg in LEGS }
PIN_LIST = [0,1,2, 3,4,5, 6,7,8, 9,10,11]

# -----------------------------
# Linkage lengths (millimeters)
# -----------------------------
COXA_LEN  = 33
FEMUR_LEN = 48
TIBIA_LEN = 80

MAX_REACH = FEMUR_LEN + TIBIA_LEN  # 128mm
PIVOT_OFFSET = 15.0          # belly → pivot height
FLOOR_DROP = MAX_REACH - PIVOT_OFFSET  # 113mm

# per-leg values (recommended)
LF.servo_zero_offset =  90.0   # left servos zero points are +90° from body-forward
RF.servo_zero_offset = -90.0   # right servos zero points are -90° from body-forward
RR.servo_zero_offset = -90.0
LR.servo_zero_offset =  90.0

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
SERVO OFFSETS OBSERVED FOR EACH UNIT (but not final values because they seem to act different when in ACTUAL use)
LF
    pin_coxa=0, NEW
    pin_femur=1,-75 straight up, 90 (45 degrees downward)
    pin_tibia=2, 90 fully inward, -90 fully extended

RF
    pin_coxa=3, NEW
    pin_femur=4, NEW
    pin_tibia=5, 90 fully inward, -90 fully extended

RR
    pin_coxa=6, NEW
    pin_femur=7,-75 straight up, 90 (30 degrees downward)
    pin_tibia=8, 90 fully inward, -90 fully extended

LR
    pin_coxa=9, NEW
    pin_femur=10, -45 straight up, 90 (45 degrees downward)
    pin_tibia=11, 90 fully inward, -90 fully extended


"""
