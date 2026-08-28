import math
from crawler.bno08x.i2c import IMUDriver
from crawler.bno08x.enable_imu_reports import configure_imu
from crawler.bno08x.imu_interpreter import IMUInterpreter


class HalIMU:
    def __init__(self):
        self.imu = IMUDriver(i2c_bus=1, address=0x4B)
        configure_imu(self.imu, interval_us=20000)

        self.interpreter = IMUInterpreter()
        self.last_pitch = 0.0
        self.last_roll = 0.0
        print("[HAL_IMU] Custom BNO08x driver stack started")


    def get_pitch_roll(self) -> dict:
        try:
            target_report = None

            # Drain packet buffer to get the latest report and prevent lag
            while True:
                pkt_obj = self.imu.read_packet()
                if not pkt_obj:
                    break

                decoded_report = self.interpreter.interpret(pkt_obj)
                if not decoded_report:
                    continue

                reports = decoded_report if isinstance(decoded_report, list) else [decoded_report]

                for r in reports:
                    if not isinstance(r, dict):
                        continue

                    # Handle IMU reset event
                    if r.get('type') == 'hub_event' and r.get('event_id') == 1:
                        print("[HAL_IMU] IMU reset event detected.")
                        self.recover()
                        return {"pitch": 0.0, "roll": 0.0}

                    # Capture latest rotation vector
                    if r.get('type') == 'game_rotation_vector':
                        target_report = r

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
            pitch = math.asin(max(-1.0, min(1.0, sinp)))

            self.last_pitch = round(math.degrees(pitch), 2)
            self.last_roll = round(math.degrees(roll), 2)

            return {"pitch": self.last_pitch, "roll": self.last_roll}

        except Exception as e:
            print(f"[HAL_IMU] Error reading IMU: {e}")
            return {"pitch": self.last_pitch, "roll": self.last_roll}

    def recover(self):
        print("[HAL_IMU] Reconfiguring IMU after reset...")
        configure_imu(self.imu, interval_us=20000)
        print("[HAL_IMU] IMU stream restored.")
