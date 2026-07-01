class SignificantMotionDecoder:
    @staticmethod
    def decode(buf):
        event = buf[2]
        return {
            "type": "significant_motion",
            "event": event
        }
