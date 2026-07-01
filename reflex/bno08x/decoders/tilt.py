class TiltDecoder:
    @staticmethod
    def decode(buf):
        event = buf[2]
        detail = buf[3]

        return {
            'type': 'tilt',
            'event': event,
            'detail': detail
        }
