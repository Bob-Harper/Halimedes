# crawler/halcrawler_v3.py
import math
from cerebellum.robot import Robot
from crawler.hal_hardware import HalLegs, Robot_Values
from crawler.arthropod_ik import ArthropodIK

class HalCrawler(Robot):
    """
    Main coordination layer operating on a UNIFORM BODY-ORIENTED LOCAL GRID.
    +dx = Forward | -dx = Backward
    +dy = Left    | -dy = Right
    -dz = Stand Depth Below Body (Pushes feet DOWN to support weight)
    +dz = Lift Height Above Floor (Picks feet UP into the air)
    """
    def __init__(self, **kwargs):
        self.legs_cfg = HalLegs()
        self.robot_cfg = Robot_Values()
        self.ik_solver = ArthropodIK(
            coxa_len=self.legs_cfg.COXA_LEN,
            femur_len=self.legs_cfg.FEMUR_LEN,
            tibia_len=self.legs_cfg.TIBIA_LEN
        )
        # Stores historical orientation frames to detect duplicated updates.
        self.prev_pitch = None
        self.prev_roll = None

        # cache of last servo angles for governor to reduce servo power draw spikes
        self.prev_pin_payload = [0.0] * 12

        pin_list = self.legs_cfg.PIN_LIST
        init_angles = [0.0] * 12
        super().__init__(pin_list=pin_list, init_angles=init_angles, **kwargs)

    def translate_ik_to_servo(self, leg_name: str, ik_angles: list) -> dict:
        leg = self.legs_cfg.LEG_MAP[leg_name]
        ik_coxa, ik_femur, ik_tibia = ik_angles
        is_left_side = leg_name in ["LF", "LR"]

        if is_left_side:
            corrected_coxa = ik_coxa - 90.0
            servo_coxa = 0.0 + corrected_coxa
        else:
            corrected_coxa = ik_coxa + 90.0
            servo_coxa = 0.0 + corrected_coxa

        zero_femur = leg["joint_zero"]["femur"] if leg["joint_zero"]["femur"] != 90.0 else 0.0
        zero_tibia = leg["joint_zero"]["tibia"]  # no special-case 90→0

        servo_femur = zero_femur - (0.0 - ik_femur)
        servo_tibia = zero_tibia - ik_tibia      # → 90 - ik_tibia

        return {
            "coxa":  max(-90.0, min(90.0, round(servo_coxa, 2))),
            "femur": max(-90.0, min(90.0, round(servo_femur, 2))),
            "tibia": max(-90.0, min(90.0, round(servo_tibia, 2)))
        }

    def execute_local_step(self, body_aligned_targets: dict, speed: int = 20, imu_data: dict = None):
        """
        Accepts targets. Automatically shifts Z using self.legs_cfg.PIVOT_OFFSET.
        Filters out duplicated background telemetry entries natively to stop servo twitches.
        """
        # 1. Pull the raw angles from your driver container dictionary safely
        current_pitch = imu_data.get("pitch", 0.0) if imu_data else 0.0
        current_roll  = imu_data.get("roll", 0.0) if imu_data else 0.0

        # =====================================================================
        # THE CORE STABILITY CHANGE GATE
        # If the incoming orientation matches the historical cache frame, it's
        # a duplicate or background report. Abort immediately to prevent
        # bus stutters and protect the servos from phantom micro-movements.
        # =====================================================================
        if current_pitch == self.prev_pitch and current_roll == self.prev_roll:
            return  # Drop out of the function cleanly, saving execution cycles

        # Secure the current values in your instance cache memory parameters
        self.prev_pitch = current_pitch
        self.prev_roll = current_roll

        pin_payload = [0.0] * 12
        MIN_SAFE_RADIUS = 90.0

        # Convert values to clean radians for your inverse trigonometry
        pitch_rad = math.radians(current_pitch)
        roll_rad  = math.radians(current_roll)

        for leg_name, coords in body_aligned_targets.items():
            leg_cfg = self.legs_cfg.LEG_MAP[leg_name]

            # Structural proximity firewall
            world_radius = math.sqrt(coords["dx"]**2 + coords["dy"]**2)
            if world_radius < MIN_SAFE_RADIUS:
                scale_factor = MIN_SAFE_RADIUS / world_radius
                safe_dx = coords["dx"] * scale_factor
                safe_dy = coords["dy"] * scale_factor
            else:
                safe_dx = coords["dx"]
                safe_dy = coords["dy"]

            # --- INVERSE BODY ROTATION FOR TRUE LEVELING ---
            # Apply inverse pitch (rotate around Y)
            dx2 =  safe_dx * math.cos(pitch_rad) + coords["dz"] * math.sin(pitch_rad)
            dz2 = -safe_dx * math.sin(pitch_rad) + coords["dz"] * math.cos(pitch_rad)

            # Apply inverse roll (rotate around X)
            dy2 =  safe_dy * math.cos(roll_rad) - dz2 * math.sin(roll_rad)
            dz3 =  safe_dy * math.sin(roll_rad) + dz2 * math.cos(roll_rad)

            # Replace safe_dx/safe_dy and stabilized dz with rotated versions
            safe_dx = dx2
            safe_dy = dy2
            rotated_dz = dz3


            # Direct geometric lever arms straight out of hardware config
            pitch_offset = leg_cfg["mount_x"] * math.sin(pitch_rad) * self.robot_cfg.PITCH_SCALE
            roll_offset  = leg_cfg["mount_y"] * math.sin(roll_rad) * self.robot_cfg.ROLL_SCALE

            # Combine the raw spatial vectors
            imu_dz_offset = pitch_offset + roll_offset

            # Use your proven, un-twisted cross-diagonal directional assignment matrix
            if leg_name in ["RF", "LR"]:
                stabilized_dz = rotated_dz + imu_dz_offset
            else:
                stabilized_dz = rotated_dz - imu_dz_offset

            # Pull structural hardware offset dynamically from your config class
            corrected_z = stabilized_dz - self.legs_cfg.PIVOT_OFFSET

            hip_dx = safe_dx - leg_cfg["mount_x"]
            hip_dy = safe_dy - leg_cfg["mount_y"]

            # print("IK INPUT:", leg_name, hip_dx, hip_dy, corrected_z)

            raw_ik = self.ik_solver.solve_leg_triangle(
                dx=hip_dx,
                dy=hip_dy,
                dz=corrected_z
            )

            translated = self.translate_ik_to_servo(leg_name, raw_ik)

            pin_payload[leg_cfg["pin_coxa"]]  = translated["coxa"]
            pin_payload[leg_cfg["pin_femur"]] = translated["femur"]
            pin_payload[leg_cfg["pin_tibia"]] = translated["tibia"]

        self.servo_write_governed(pin_payload)

    def servo_write_governed(self, target_payload):
        v = self.robot_cfg

        # scaled limits
        max_delta = v.MAX_DELTA_PER_SERVO * v.MOVEMENT_SCALER
        max_total = v.MAX_TOTAL_DELTA * v.MOVEMENT_SCALER

        deltas = [
            target_payload[i] - self.prev_pin_payload[i]
            for i in range(12)
        ]

        # per-servo clamp
        clamped = [
            max(-max_delta, min(max_delta, d))
            for d in deltas
        ]

        # total movement clamp
        total = sum(abs(d) for d in clamped)
        if total > max_total:
            scale = max_total / total
            clamped = [d * scale for d in clamped]

        governed_payload = [
            self.prev_pin_payload[i] + clamped[i]
            for i in range(12)
        ]

        self.servo_write_raw(governed_payload)
        self.prev_pin_payload = governed_payload
