#     0x05: 14,	# Rotation Vector
# The units for the accuracy estimate are radians.
# The Q point is 12

class RotationVectorDecoder:
    @staticmethod
    def decode(buf):
        # buf[0] = 0x05
        # buf[1] = sequence (ignore)

        i_raw = int.from_bytes(buf[4:6], 'little', signed=True)
        j_raw = int.from_bytes(buf[6:8], 'little', signed=True)
        k_raw = int.from_bytes(buf[8:10], 'little', signed=True)
        r_raw = int.from_bytes(buf[10:12], 'little', signed=True)

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

"""
Byte Description
0 Report ID = 0x05
1 Sequence number
2 Status
3 Delay
4 Unit quaternion i component LSB
5 Unit quaternion i component MSB
6 Unit quaternion j component LSB
7 Unit quaternion j component MSB
8 Unit quaternion k component LSB
9 Unit quaternion k component MSB
10 Unit quaternion real component LSB
11 Unit quaternion real component MSB
12 Accuracy estimate LSB
13 Accuracy estimate MSB
"""
