class TapDecoder:

    @staticmethod
    def decode(buf):
        tap_type = buf[2]
        direction = buf[3]

        return {
            'type': 'tap',
            'tap_type': tap_type,
            'direction': direction
        }
