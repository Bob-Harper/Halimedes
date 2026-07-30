#     0x08: 12,
# Game Rotation Vector
# The Q point is 14

class GameRotationVectorDecoder:
    @staticmethod
    def decode(buf):
        i_raw = int.from_bytes(buf[4:6], 'little', signed=True)
        j_raw = int.from_bytes(buf[6:8], 'little', signed=True)
        k_raw = int.from_bytes(buf[8:10], 'little', signed=True)
        r_raw = int.from_bytes(buf[10:], 'little', signed=True)

        scale = 16384.0  # Q14

        return {
            'type': 'game_rotation_vector',
            'i': i_raw / scale,
            'j': j_raw / scale,
            'k': k_raw / scale,
            'real': r_raw / scale
        }

        return {
            'type': 'game_rotation_vector',
            'i': i,
            'j': j,
            'k': k,
            'real': r
        }

"""
Byte Description
0 Report ID = 0x08                      1
1 Sequence number                       2
2 Status                                3
3 Delay                                 4
4 Unit quaternion i component LSB       5
5 Unit quaternion i component MSB       6
6 Unit quaternion j component LSB       7
7 Unit quaternion j component MSB       8
8 Unit quaternion k component LSB       9
9 Unit quaternion k component MSB       10
10 Unit quaternion real component LSB   11
11 Unit quaternion real component MSB   12
"""
