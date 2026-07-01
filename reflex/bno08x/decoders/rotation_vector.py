class RotationVectorDecoder:
    @staticmethod
    def decode(buf):
        # buf[0] = 0x05
        # buf[1] = sequence (ignore)

        i_raw = int.from_bytes(buf[2:4], 'little', signed=True)
        j_raw = int.from_bytes(buf[4:6], 'little', signed=True)
        k_raw = int.from_bytes(buf[6:8], 'little', signed=True)
        r_raw = int.from_bytes(buf[8:10], 'little', signed=True)

        i = i_raw / 16384.0
        j = j_raw / 16384.0
        k = k_raw / 16384.0
        r = r_raw / 16384.0

        return {
            'type': 'rotation_vector',
            'i': i,
            'j': j,
            'k': k,
            'real': r
        }