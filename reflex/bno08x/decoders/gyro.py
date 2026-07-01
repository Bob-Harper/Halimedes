class GyroDecoder:
    @staticmethod
    def decode(buf):
        # buf[0] = 0x02
        # buf[1] = sequence number (ignore)

        x_raw = int.from_bytes(buf[2:4], 'little', signed=True)
        y_raw = int.from_bytes(buf[4:6], 'little', signed=True)
        z_raw = int.from_bytes(buf[6:8], 'little', signed=True)

        x = x_raw / 256.0
        y = y_raw / 256.0
        z = z_raw / 256.0

        return {
            'type': 'gyro',
            'x': x,
            'y': y,
            'z': z
        }

