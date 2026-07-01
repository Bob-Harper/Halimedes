class ShakeDecoder:
    @staticmethod
    def decode(buf):
        event = buf[2]
        strength = buf[3]

        return {
            'type': 'shake',
            'event': event,
            'strength': strength
        }