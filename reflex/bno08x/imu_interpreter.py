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
from .decoders.sig_motion import SignificantMotionDecoder
from .decoders.tap import TapDecoder

class IMUInterpreter:
    def interpret(self, pkt):
        buf = pkt.data  # raw bytes

        # unwrap BASE_TIMESTAMP packets
        if buf[0] == 0xFB:
            buf = buf[6:]  # skip timestamp header

        report_id = buf[0]
        # NOTE:
        # The SH-2 IMU can emit multi-report frames, where a BASE_TIMESTAMP (0xFB)
        # packet contains more than one logical sensor report. This interpreter
        # intentionally decodes only the first meaningful report after the timestamp
        # header (buf[6:]).
        #
        # Additional embedded reports may be present in the remaining bytes, but
        # they are not handled at this time. If Hal appears to ignore certain
        # events or sensor states, it may be because those reports were included
        # in a multi-report frame and were not decoded.
        #
        # Future enhancement: add support for parsing multiple embedded reports
        # within a single packet.
        if report_id == 0x05:
            return RotationVectorDecoder.decode(buf)

        if report_id == 0x08:
            return GameRotationVectorDecoder.decode(buf)

        if report_id == 0x06:
            return GravityDecoder.decode(buf)

        if report_id == 0x04:
            return LinearAccelDecoder.decode(buf)

        if report_id == 0x02:
            return GyroDecoder.decode(buf)

        if report_id == 0x01:
            return AccelDecoder.decode(buf)

        if report_id == 0x03:
            return MagDecoder.decode(buf)

        if report_id == 0x13:
            return StabilityDecoder.decode(buf)

        if report_id == 0x20:
            return TiltDecoder.decode(buf)

        if report_id == 0x19:
            return ShakeDecoder.decode(buf)

        if report_id == 0x1A:
            return FlipDecoder.decode(buf)

        if report_id == 0x1B:
            return PickupDecoder.decode(buf)

        if report_id == 0x12:
            return SignificantMotionDecoder.decode(buf)

        if report_id == 0x10:
            return TapDecoder.decode(buf)

        return None
