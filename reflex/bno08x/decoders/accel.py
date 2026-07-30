#     0x01: 10,
# Accelerometer
# The units are m/s^2
# The Q point is 8.

class AccelDecoder:
    @staticmethod
    def decode(buf):
        # Q8.8 fixed point: value = raw / 256.0
        ax = int.from_bytes(buf[4:6], 'little', signed=True) / 256.0
        ay = int.from_bytes(buf[6:8], 'little', signed=True) / 256.0
        az = int.from_bytes(buf[8:], 'little', signed=True) / 256.0

        return {
            "type": "accel",
            "x": ax,
            "y": ay,
            "z": az
        }

"""
Byte    Description
0       Report ID = 0x01
1       Sequence number
2       Status
3       Delay
4       Accelerometer Axis X LSB
5       Accelerometer Axis X MSB
6       Accelerometer Axis Y LSB
7       Accelerometer Axis Y MSB
8       Accelerometer Axis Z LSB
9       Accelerometer Axis Z MSB
"""