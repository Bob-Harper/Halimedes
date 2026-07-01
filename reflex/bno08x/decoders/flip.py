class FlipDecoder:
    @staticmethod
    def decode(buf):
        event = buf[2]
        direction = buf[3]

        return {
            'type': 'flip',
            'event': event,
            'direction': direction
        }