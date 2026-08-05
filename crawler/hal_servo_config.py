# crawler/hal_servo_config.py

from dataclasses import dataclass

@dataclass
class ServoSet:
    name: str
    pin_coxa: int
    pin_femur: int
    pin_tibia: int
    coxa_dir: int
    femur_dir: int
    tibia_dir: int

# ---------------------------------------------------------
# Servo pin assignments (Robot HAT / PCA9685 channels)
# ---------------------------------------------------------

LF = ServoSet(
    name="LF",
    pin_coxa=5,
    pin_femur=4,
    pin_tibia=3,
    coxa_dir=1,
    femur_dir=1,
    tibia_dir=-1
)

RF = ServoSet(
    name="RF",
    pin_coxa=11,
    pin_femur=10, # giving trouble
    pin_tibia=9,
    coxa_dir=1,
    femur_dir=1,
    tibia_dir=1
)

RR = ServoSet(
    name="RR",
    pin_coxa=8,
    pin_femur=7,
    pin_tibia=6,
    coxa_dir=1,
    femur_dir=1,
    tibia_dir=-1
)

LR = ServoSet(
    name="LR",
    pin_coxa=2,
    pin_femur=1,
    pin_tibia=0,
    coxa_dir=1,
    femur_dir=1,
    tibia_dir=1
)

SERVOS = [LF, RF, RR, LR]
PIN_LIST = [5,4,3, 11,10,9, 8,7,6, 2,1,0]

SERVOS = [LF, RF, RR, LR]
PIN_LIST = [5,4,3, 11,10,9, 8,7,6, 2,1,0]