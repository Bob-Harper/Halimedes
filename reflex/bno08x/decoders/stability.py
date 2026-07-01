class StabilityDecoder:
    @staticmethod
    def decode(buf):
        state = buf[2]
        return {
            "type": "stability",
            "state": state
        }