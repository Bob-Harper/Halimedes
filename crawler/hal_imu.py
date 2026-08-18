# crawler/hal_imu.py
import math
from reflex.bno08x.i2c import IMUDriver
from reflex.bno08x.enable_imu_reports import configure_imu
from reflex.bno08x.imu_interpreter import IMUInterpreter

class HalIMU:
    """
    Direct hardware interface wrapper utilizing your local reflex driver stack.
    Configured for a safe, crash-free 50Hz timing profile to eliminate I2C bus stress.
    """
    def __init__(self):
        try:
            self.imu = IMUDriver(i2c_bus=1, address=0x4B)

            # =================================================================
            # TIMING CALIBRATION: Changed interval from 10000us (100Hz) to 20000us (50Hz).
            # This completely solves the clock-stretching watchdog reset bug.
            # =================================================================
            configure_imu(self.imu, interval_us=20000)

            self.interpreter = IMUInterpreter()
            self.connected = True

            self.last_pitch = 0.0
            self.last_roll = 0.0
            print("[HAL_IMU] Custom BNO08x driver stack attached at stable 50Hz.")
        except Exception as e:
            print(f"[HAL_IMU ERROR] Failed to anchor local hardware driver stream: {e}")
            self.connected = False

    def get_pitch_roll(self) -> dict:
        if not self.connected:
            return {"pitch": 0.0, "roll": 0.0}

        try:
            pkt_obj = self.imu.read_packet()
            if not pkt_obj:
                return {"pitch": self.last_pitch, "roll": self.last_roll}

            decoded_report = self.interpreter.interpret(pkt_obj)
            if decoded_report is None:
                return {"pitch": self.last_pitch, "roll": self.last_roll}

            target_report = None
            if isinstance(decoded_report, list):
                for r in decoded_report:
                    if isinstance(r, dict) and r.get('type') == 'game_rotation_vector':
                        target_report = r
                        break
            elif isinstance(decoded_report, dict) and decoded_report.get('type') == 'game_rotation_vector':
                target_report = decoded_report

            if target_report is None:
                return {"pitch": self.last_pitch, "roll": self.last_roll}

            qi = target_report.get('i', 0.0)
            qj = target_report.get('j', 0.0)
            qk = target_report.get('k', 0.0)
            qr = target_report.get('real', 1.0)

            sinr_cosp = 2.0 * (qr * qi + qj * qk)
            cosr_cosp = 1.0 - 2.0 * (qi * qi + qj * qj)
            roll = math.atan2(sinr_cosp, cosr_cosp)

            sinp = 2.0 * (qr * qj - qk * qi)
            pitch = math.asin(sinp) if abs(sinp) < 1 else math.copysign(math.pi / 2.0, sinp)

            self.last_pitch = round(math.degrees(pitch), 2)
            self.last_roll = round(math.degrees(roll), 2)

            return {"pitch": self.last_pitch, "roll": self.last_roll}

        except Exception:
            return {"pitch": self.last_pitch, "roll": self.last_roll}
