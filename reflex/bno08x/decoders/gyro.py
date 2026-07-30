#     0x02: 10,
# Gyroscope Calibrated
# The Q point is 9.

class GyroDecoder:
    @staticmethod
    def decode(buf):
        # buf[0] = 0x02
        # buf[1] = sequence number (ignore)

        x_raw = int.from_bytes(buf[4:6], 'little', signed=True)
        y_raw = int.from_bytes(buf[6:8], 'little', signed=True)
        z_raw = int.from_bytes(buf[8:], 'little', signed=True)

        x = x_raw / 256.0
        y = y_raw / 256.0
        z = z_raw / 256.0

        return {
            'type': 'gyro',
            'x': x,
            'y': y,
            'z': z
        }

"""
Byte Description
0 Report ID = 0x02
1 Sequence number
2 Status
3 Delay
4 Gyroscope calibrated Axis X LSB
5 Gyroscope calibrated Axis X MSB
6 Gyroscope calibrated Axis Y LSB
7 Gyroscope calibrated Axis Y MSB
8 Gyroscope calibrated Axis Z LSB
9 Gyroscope calibrated Axis Z MSB
"""
