# reflex/bno08x/imu_interpreter.py

from .decoders.rotation_vector import RotationVectorDecoder
from .decoders.game_rotation_vector import GameRotationVectorDecoder
from .decoders.gravity import GravityDecoder
from .decoders.linear_accel import LinearAccelDecoder
from .decoders.gyro import GyroDecoder
from .decoders.accel import AccelDecoder
from .decoders.mag import MagDecoder
import time


REPORT_LENGTHS = {
    0x01: 10,  # Accelerometer
    0x02: 10,  # Gyroscope Calibrated
    0x03: 10,  # Magnetic Field Calibrated
    0x04: 10,  # Linear Acceleration
    0x05: 14,  # Rotation Vector
    0x06: 10,  # Gravity
    0x08: 12,  # Game Rotation Vector
}

class IMUInterpreter:
    def __init__(self):
        self.log_data = False

    def interpret(self, pkt):
        # Normalize Packet → bytes
        if hasattr(pkt, "data"):
            buf = pkt.data
        else:
            buf = pkt

        # Optional logging of raw FB packets
        if self.log_data and buf and buf[0] == 0xFB:
            import time
            with open("data/sensor_packet.log", "a") as f:
                ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + f".{int(time.time() * 1000) % 1000:03d}"
                f.write("\n\n==================== BEGIN PACKET ====================\n")
                f.write(f"{ts}\n")
                f.write(" ".join(f"{b:02X}" for b in buf))
                f.write("\n==================== END PACKET ====================\n\n")

        # --- Strict timestamp stripping ---

        # Require FB at start; if not, packet is unusable
        if not buf or buf[0] != 0xFB or len(buf) < 5:
            return None

        # Strip FB (5 bytes)
        buf = buf[5:]

        # If FA is present next, strip it too (5 bytes)
        if buf and buf[0] == 0xFA:
            if len(buf) < 5:
                return None
            buf = buf[5:]

        # Now buf[0] MUST be a valid report ID
        if not buf:
            return None

        report_id = buf[0]
        if report_id not in REPORT_LENGTHS:
            return None

        length = len(buf)
        idx = 0
        reports = []

        # Multi-report loop, but strictly from the start, no scanning
        while idx < length:
            report_id = buf[idx]

            # If we hit something that isn't a known report, stop
            if report_id not in REPORT_LENGTHS:
                break

            payload_size = REPORT_LENGTHS[report_id]
            end = idx + payload_size

            # If we don't have enough bytes for this report, stop
            if end > length:
                break

            report_buf = buf[idx:end]

            decoded = None
            if report_id == 0x01:
                decoded = AccelDecoder.decode(report_buf)
            elif report_id == 0x02:
                decoded = GyroDecoder.decode(report_buf)
            elif report_id == 0x03:
                decoded = MagDecoder.decode(report_buf)
            elif report_id == 0x04:
                decoded = LinearAccelDecoder.decode(report_buf)
            elif report_id == 0x05:
                decoded = RotationVectorDecoder.decode(report_buf)
            elif report_id == 0x06:
                decoded = GravityDecoder.decode(report_buf)
            elif report_id == 0x08:
                decoded = GameRotationVectorDecoder.decode(report_buf)

            if decoded is not None:
                reports.append(decoded)

            idx = end

        if len(reports) == 1:
            return reports[0]
        if len(reports) > 1:
            return reports

        return None
