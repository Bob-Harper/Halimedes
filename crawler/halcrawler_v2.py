# crawler/halcrawler_v2.py
import math
from crawler.robot import Robot
from crawler.hal_leg_hardware import HalLegs
from crawler.arthropod_ik import ArthropodIK

class HalCrawler(Robot):
    """
    The final coordination bridge for the quadruped.
    Operates strictly on a UNIFORM BODY-ORIENTED LOCAL GRID shifted to each hip:
    +dx = Forward  | -dx = Backward
    +dy = Left     | -dy = Right
    -dz = Lift UP  | +dz = Push DOWN
    """
    def __init__(self, **kwargs):
        self.legs_cfg = HalLegs()
        self.ik_solver = ArthropodIK(
            coxa_len=self.legs_cfg.COXA_LEN,
            femur_len=self.legs_cfg.FEMUR_LEN,
            tibia_len=self.legs_cfg.TIBIA_LEN
        )

        pin_list = self.legs_cfg.PIN_LIST
        init_angles = [0.0] * 12
        super().__init__(pin_list=pin_list, init_angles=init_angles, **kwargs)

    def translate_ik_to_servo(self, leg_name: str, ik_angles: list) -> dict:
        """
        Takes raw math angles from the body-aligned IK engine and maps them
        directly to your clean -90 to 90 hardware space.
        """
        leg = self.legs_cfg.LEG_MAP[leg_name]
        ik_coxa, ik_femur, ik_tibia = ik_angles

        is_left_side = leg_name in ["LF", "LR"]

        # =====================================================================
        # 1. COXA AXIS MAPPING (Straight out = 0.0 hardware baseline)
        # =====================================================================
        if is_left_side:
            corrected_coxa = ik_coxa - 90.0
            servo_coxa = 0.0 + corrected_coxa
        else:
            corrected_coxa = ik_coxa + 90.0
            servo_coxa = 0.0 + corrected_coxa

        # =====================================================================
        # 2. FEMUR TRANSLATION (Your confirmed zero-horizon math)
        # =====================================================================
        zero_femur = leg["joint_zero"]["femur"] if leg["joint_zero"]["femur"] != 90.0 else 0.0
        servo_femur = zero_femur - (0.0 - ik_femur)

        # =====================================================================
        # 3. TIBIA TRANSLATION
        # =====================================================================
        zero_tibia = leg["joint_zero"]["tibia"] if leg["joint_zero"]["tibia"] != 90.0 else 0.0
        servo_tibia = zero_tibia - ik_tibia

        return {
            "coxa":  max(-90.0, min(90.0, round(servo_coxa, 2))),
            "femur": max(-90.0, min(90.0, round(servo_femur, 2))),
            "tibia": max(-90.0, min(90.0, round(servo_tibia, 2)))
        }

    def execute_local_step(self, body_aligned_targets: dict, speed: int = 20, bpm: float = None):
        """
        Accepts targets where -dz explicitly lifts the foot up.
        Enforces a hard radial safety barrier to protect chassis servos and IR sensors.
        """
        pin_payload = [0.0] * 12

        # Hard mechanical safety threshold from body center (0,0)
        MIN_SAFE_RADIUS = 90.0  # Safe clearance zone

        for leg_name, coords in body_aligned_targets.items():
            leg_cfg = self.legs_cfg.LEG_MAP[leg_name]

            # Calculate the true horizontal distance from the center of the robot body
            world_radius = math.sqrt(coords["dx"]**2 + coords["dy"]**2)

            # Firewall: If the high-level gait tries to pull a leg too close,
            # we automatically clamp its outward extension safely at your threshold.
            if world_radius < MIN_SAFE_RADIUS:
                print(f"[SAFETY WARN] {leg_name} requested unsafe position ({coords['dx']}, {coords['dy']}). Radius {world_radius:.1f}mm is too tight! Clamping to {MIN_SAFE_RADIUS}mm.")

                # Proportional scaling to push the target out along the same vector
                scale_factor = MIN_SAFE_RADIUS / world_radius
                safe_dx = coords["dx"] * scale_factor
                safe_dy = coords["dy"] * scale_factor
            else:
                safe_dx = coords["dx"]
                safe_dy = coords["dy"]

            # Process with the secured, safe coordinates
            corrected_z = -coords["dz"]

            raw_ik = self.ik_solver.solve_leg_triangle(
                dx=safe_dx,
                dy=safe_dy,
                dz=corrected_z
            )

            translated = self.translate_ik_to_servo(leg_name, raw_ik)

            pin_payload[leg_cfg["pin_coxa"]]  = translated["coxa"]
            pin_payload[leg_cfg["pin_femur"]] = translated["femur"]
            pin_payload[leg_cfg["pin_tibia"]] = translated["tibia"]

        self.servo_move(pin_payload, speed=speed, bpm=bpm)
