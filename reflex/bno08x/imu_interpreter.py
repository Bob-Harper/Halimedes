from .decoders.rotation_vector import RotationVectorDecoder
from .decoders.game_rotation_vector import GameRotationVectorDecoder
from .decoders.gravity import GravityDecoder
from .decoders.linear_accel import LinearAccelDecoder
from .decoders.gyro import GyroDecoder
from .decoders.accel import AccelDecoder
from .decoders.mag import MagDecoder
from .decoders.stability import StabilityDecoder
from .decoders.tilt import TiltDecoder
from .decoders.shake import ShakeDecoder
from .decoders.flip import FlipDecoder
from .decoders.pickup import PickupDecoder
from .decoders.tap import TapDecoder

        # NOTE:
        # The SH-2 IMU can emit multi-report frames, where a BASE_TIMESTAMP (0xFB)
        # packet contains more than one logical sensor report. This interpreter
        # intentionally decodes only the first meaningful report after the timestamp
        # header (buf[6:]).
        #
        # Additional embedded reports may be present in the remaining bytes, and
        # the IMUInterpreter class is designed to decode all of them, returning a
        # list of decoded reports if multiple are found.

class IMUInterpreter:
    def interpret(self, pkt):
        # Defensive: malformed packet → ignore
        try:
            buf = pkt.data
        except Exception:
            return None

        if not buf or len(buf) < 2:
            return None

        # Unwrap BASE_TIMESTAMP packets
        if buf[0] == 0xFB:
            if len(buf) < 7:
                return None
            buf = buf[6:]  # skip timestamp header

        # After unwrap, buf may contain multiple reports
        reports = []
        idx = 0
        length = len(buf)

        while idx < length:
            # Each report must have at least 2 bytes: id + seq
            if idx + 2 > length:
                break

            report_id = buf[idx]
            seq = buf[idx + 1]

            # Determine payload size based on report_id
            # All your decoders use fixed 8‑byte payloads (except quaternions: 10 bytes)
            # We map them directly.

            if report_id in (0x01, 0x02, 0x03, 0x04, 0x06, 0x13, 0x19, 0x1A, 0x1B, 0x10, 0x20):
                payload_size = 8  # accel, gyro, mag, linear, gravity, stability, shake, flip, pickup, tap, tilt

            elif report_id in (0x05, 0x08):
                payload_size = 10  # rotation_vector, game_rotation_vector

            else:
                # Unknown report → skip 1 byte and continue
                idx += 1
                continue

            # Ensure payload fits
            end = idx + 2 + payload_size
            if end > length:
                break

            # Slice the report
            report_buf = buf[idx:end]

            # Decode safely
            decoded = None
            try:
                if report_id == 0x05:
                    decoded = RotationVectorDecoder.decode(report_buf)
                elif report_id == 0x08:
                    decoded = GameRotationVectorDecoder.decode(report_buf)
                elif report_id == 0x06:
                    decoded = GravityDecoder.decode(report_buf)
                elif report_id == 0x04:
                    decoded = LinearAccelDecoder.decode(report_buf)
                elif report_id == 0x02:
                    decoded = GyroDecoder.decode(report_buf)
                elif report_id == 0x01:
                    decoded = AccelDecoder.decode(report_buf)
                elif report_id == 0x03:
                    decoded = MagDecoder.decode(report_buf)
                elif report_id == 0x13:
                    decoded = StabilityDecoder.decode(report_buf)
                elif report_id == 0x20:
                    decoded = TiltDecoder.decode(report_buf)
                elif report_id == 0x19:
                    decoded = ShakeDecoder.decode(report_buf)
                elif report_id == 0x1A:
                    decoded = FlipDecoder.decode(report_buf)
                elif report_id == 0x1B:
                    decoded = PickupDecoder.decode(report_buf)
                elif report_id == 0x10:
                    decoded = TapDecoder.decode(report_buf)
            except Exception:
                decoded = None

            if decoded is not None:
                reports.append(decoded)

            # Advance to next embedded report
            idx = end

        # If only one report, return it directly
        if len(reports) == 1:
            return reports[0]

        # If multiple reports, return list
        if len(reports) > 1:
            return reports

        return None
