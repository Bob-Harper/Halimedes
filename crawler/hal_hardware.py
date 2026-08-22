# crawler/hal_hardware.py


class Headlights:
    """
    Repurposes Mot0rport1 fors use as brightness control for front mounted headlights/searchlight.
    Motorport2 pins are already repurposed elsewhere and cannot be used as a hardware control at this time.
    """
    def __init__(self):
        self.period = 4095
        self.prescaler = 10
        freq=100
        self.motor_1_pwm_pin = "P13"
        self.motor_1_dir_pin = "D4"


class PWM_Values:
    """
    CO-PROCESSOR PWM HARDWARE CONFIGURATION
    Static baseline constraints of the expansion hat's MCU core
    """
    def __init__(self):
        self.PWM_CLOCK = 72000000.0  # Internal 72MHz hardware clock speed
        self.PWM_DEFAULT_FREQ = 50   # 50Hz Standard servo baseline refresh cycle
        self.REG_PWM_CHN = 0x20      # Duty cycle channel register base address
        self.REG_PWM_PSC = 0x40      # Prescaler register base address
        self.REG_PWM_ARR = 0x44      # Auto-reload / Period register base address
        self.PWM_ADDR = [0x14, 0x15] # I2C slave address map for the MCU hat


class Servo_Values:
    """
    SERVO HARDWARE SPECIFICATION CONSTANTS
    Defines absolute mechanical boundary conditions and pulse width modulations.
    Operates independently from inverse kinematics and chip register prefixes.
    See bottom of this page for the Coreless servo specs.
    """
    def __init__(self):
        self.MIN_PW = 500   # Minimum pulse width in microseconds (Full CCW)
        self.MAX_PW = 2500  # Maximum pulse width in microseconds (Full CW)
        self.SERVO_FREQ = 50        # Hardcoded 50Hz refresh baseline frame
        self.SERVO_PERIOD = 4095    # 12-bit absolute resolution ceiling (0-4095)
        self.FRAME_US = 20000.0


class Robot_Values:
    """
    MASTER HARDWARE POSTURE CONSTANTS FOR HAL

    Tuned for high-speed physical operation (720°/s MAX DPS limit).
    Logical speed range scale is mapped to 0-200. Speed=100 matches the
    previous maximum speed at 428°/s, while values up to 200 activate the
    servo overdrive headroom up to the physical maximum achievable hardware limit.

    WARNING: Movements calling direct, massive servo angle adjustments must
    be carefully monitored. Simultaneous multi-joint adjustments can cause
    severe voltage underruns when speeds exceed 25.
    """
    def __init__(self):
        self.MAX_DPS = 720.0
        self.SERVO_COUNT = 12
        self.PIN_COUNT = 12
        self.STEP_TIME_MS = 10.0  # 10ms internal step interpolation interval
        self.SPEED_SCALE_NORM = 100 # Sane Speed in most movments is calibrated for 1-100.
        self.SPEED_SCALE_MAX = 200 # Values up to this allows for a "Turbo Mode"

class HalLegs:
    """
    Hardware Specification Matrix for Hal.
    Contains absolute physical dimensions, pin maps, and hardware zero-points.
    """
    def __init__(self):
        # Linkage dimensions (mm)
        self.COXA_LEN  = 33
        self.FEMUR_LEN = 48
        self.TIBIA_LEN = 80

        # Structural space boundaries
        self.MAX_REACH = self.FEMUR_LEN + self.TIBIA_LEN
        self.PIVOT_OFFSET = 15.0  # Vertical height of femur horn above baseplate plane
        self.FLOOR_DROP = self.MAX_REACH - self.PIVOT_OFFSET

        # Definitive leg configurations
        self.LF = {
            "name": "LF",
            "mount_x": 40, "mount_y": 40, "mount_angle": 0,
            "coxa_dir": 1, "femur_dir": 1, "tibia_dir": 1,
            "pin_coxa": 0, "pin_femur": 1, "pin_tibia": 2,
            "servo_zero_offset": 0.0,
            "joint_zero": {"coxa": 90.0, "femur": 0.0, "tibia": 0.0},
            "joint_range": {"coxa": (0, 180), "femur": (-45, 90), "tibia": (-90, 90)}
        }

        self.RF = {
            "name": "RF",
            "mount_x": 40, "mount_y": -40, "mount_angle": 0,
            "coxa_dir": 1, "femur_dir": 1, "tibia_dir": 1,
            "pin_coxa": 3, "pin_femur": 4, "pin_tibia": 5,
            "servo_zero_offset": 0.0,
            "joint_zero": {"coxa": 90.0, "femur": 5.0, "tibia": 0.0},
            "joint_range": {"coxa": (0, 180), "femur": (-45, 90), "tibia": (-90, 90)}
        }

        self.RR = {
            "name": "RR",
            "mount_x": -40, "mount_y": -40, "mount_angle": 0,
            "coxa_dir": 1, "femur_dir": 1, "tibia_dir": 1,
            "pin_coxa": 6, "pin_femur": 7, "pin_tibia": 8,
            "servo_zero_offset": 0.0,
            "joint_zero": {"coxa": 90.0, "femur": 0.0, "tibia": 0.0},
            "joint_range": {"coxa": (0, 180), "femur": (-45, 90), "tibia": (-90, 90)}
        }

        self.LR = {
            "name": "LR",
            "mount_x": -40, "mount_y": 40, "mount_angle": 0,
            "coxa_dir": 1, "femur_dir": 1, "tibia_dir": 1,
            "pin_coxa": 9, "pin_femur": 10, "pin_tibia": 11,
            "servo_zero_offset": 0.0,
            "joint_zero": {"coxa": 90.0, "femur": 5.0, "tibia": 0.0},
            "joint_range": {"coxa": (0, 180), "femur": (-45, 90), "tibia": (-90, 90)}
        }

        # Collections
        self.LEGS = [self.LF, self.RF, self.RR, self.LR]
        self.LEG_MAP = {leg["name"]: leg for leg in self.LEGS}
        self.PIN_LIST = [
            self.LF["pin_coxa"], self.LF["pin_femur"], self.LF["pin_tibia"],
            self.RF["pin_coxa"], self.RF["pin_femur"], self.RF["pin_tibia"],
            self.RR["pin_coxa"], self.RR["pin_femur"], self.RR["pin_tibia"],
            self.LR["pin_coxa"], self.LR["pin_femur"], self.LR["pin_tibia"],
        ]

"""

Product description

9g Coreless Servo Black, Full Metal Gear Micro RC Servo 4KG-CM Torque 4.8-8.4V for Arduino Fixed-wing Aircraft RC Smart Car Robotic Arm DIY Projects (180 Degree)

Products Specifcation :
Products Name: 9g micro coreless servo

Apply Environmental Conditon
Storage Temperature Range: -30°C-80°C
Operating Temperature Range: -15°C-70°C
Operating Voltage Range: 4.8-8.4V

Mechanical Specifications
Size: 24*11.8*21.9mm / 0.94x0.46x0.86 in
Weight:13g
Gear type: Full Metal
Gear ratio:410
Bearing: Double Bearing
Connector wire: 170±5mm / 6.69 ±0.19 in
Motor : 3-Pole(k)
Horn gear spline: 25T
Horn type: Plastic
Case: Engineering plastics

Electrical Specifications
Operat voltage: 4.8V-8.4V
Idle current(at stopped): 4mA(6V), 5mA(7.4V), 6mA(8.4V)
Operating speed (at no load): 0.14sec/60° (6V) , 0.12sec/60°(7.4V), 0.10sec/60°(8.4V)
Stall torque (at locked): 3.5kg-cm(6V) , 4 kg-cm(7.4V), 5 kg-cm(8.4V)
Stall current (at locked):0.6A(6V), 0.8A(7.4V), 1.0A(8.4V)

Control Specifications
Control System : PWM (Pulse width modification)
Pulse width range: 500-2500μsec
Neutral position: 1500μsec
Running degree: 180°(when 500-2500μsec) / 90°（when remote control 1000-2000μsec)
Dead band width: 3 μsec
Operating frequency: 50-330Hz
Rotating direction: Counterclockwise (when 500～2500 μsec)

"""