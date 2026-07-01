class PickupDecoder:
    @staticmethod
    def decode(buf):
        event = buf[2]
        detail = buf[3]

        return {
            'type': 'pickup',
            'event': event,
            'detail': detail
        }
