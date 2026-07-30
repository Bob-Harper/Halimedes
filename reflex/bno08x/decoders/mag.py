#     0x03: 10,	# Magnetic Field Calibrated
# The units are uTesla.
# The Q point is 4.

class MagDecoder:
    @staticmethod
    def decode(buf):
        # buf[0] = 0x03
        # buf[1] = sequence (ignore)

        x_raw = int.from_bytes(buf[2:4], 'little', signed=True)
        y_raw = int.from_bytes(buf[4:6], 'little', signed=True)
        z_raw = int.from_bytes(buf[6:8], 'little', signed=True)

        x = x_raw / 256.0
        y = y_raw / 256.0
        z = z_raw / 256.0

        return {
            'type': 'mag',
            'x': x,
            'y': y,
            'z': z
        }

"""
Byte Description
0 Report ID = 0x03
1 Sequence number
2 Status
3 Delay
4 Magnetic Field calibrated Axis X LSB
5 Magnetic Field calibrated Axis X MSB
6 Magnetic Field calibrated Axis Y LSB
7 Magnetic Field calibrated Axis Y MSB
8 Magnetic Field calibrated Axis Z LSB
9 Magnetic Field calibrated Axis Z MSB
"""
