#     0x06: 10,
# Gravity
# The units are m/s^2.
# The Qpoint is 8.

class GravityDecoder:
    @staticmethod
    def decode(buf):
        # buf[0] = 0x0A
        # buf[1] = sequence number (ignore)

        x_raw = int.from_bytes(buf[4:6], 'little', signed=True)
        y_raw = int.from_bytes(buf[6:8], 'little', signed=True)
        z_raw = int.from_bytes(buf[8:], 'little', signed=True)

        x = x_raw / 256.0
        y = y_raw / 256.0
        z = z_raw / 256.0

        return {
            'type': 'gravity',
            'x': x,
            'y': y,
            'z': z
        }

"""
Byte Description
0 Report ID = 0x06
1 Sequence number
2 Status
3 Delay
4 Gravity Axis X LSB
5 Gravity Axis X MSB
6 Gravity Axis Y LSB
7 Gravity Axis Y MSB
8 Gravity Axis Z LSB
9 Gravity Axis Z MSB
"""
