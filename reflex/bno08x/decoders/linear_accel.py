#     0x04: 10,	# Linear Acceleration.
# The Q point is 8.

class LinearAccelDecoder:
    @staticmethod
    def decode(buf):
        # buf[0] = 0x04
        # buf[1] = sequence number (ignore)

        x_raw = int.from_bytes(buf[4:6], 'little', signed=True)
        y_raw = int.from_bytes(buf[6:8], 'little', signed=True)
        z_raw = int.from_bytes(buf[8:], 'little', signed=True)

        x = x_raw / 256.0
        y = y_raw / 256.0
        z = z_raw / 256.0

        return {
            'type': 'linear_accel',
            'x': x,
            'y': y,
            'z': z
        }

"""
Byte Description
0 Report ID = 0x04
1 Sequence number
2 Status
3 Delay
4 Linear acceleration Axis X LSB
5 Linear acceleration Axis X MSB
6 Linear acceleration Axis Y LSB
7 Linear acceleration Axis Y MSB
8 Linear acceleration Axis Z LSB
9 Linear acceleration Axis Z MSB
"""
