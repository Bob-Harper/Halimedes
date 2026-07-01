# ACCELEROMETER (0x01)
class AccelDecoder:
    @staticmethod
    def decode(buf):
        # Q8.8 fixed point: value = raw / 256.0
        ax = int.from_bytes(buf[2:4], 'little', signed=True) / 256.0
        ay = int.from_bytes(buf[4:6], 'little', signed=True) / 256.0
        az = int.from_bytes(buf[6:8], 'little', signed=True) / 256.0

        return {
            "type": "accel",
            "x": ax,
            "y": ay,
            "z": az
        }
