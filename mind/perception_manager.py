class PerceptionManager:
    def __init__(self):
        self.user_text = None
        self.user_emotion = None
        self.speaker = None

        self.faces = []
        self.objects = []
        self.qr_codes = []

        self.battery_level = None
        self.audio_direction = None
        self.last_action = None

    def reset(self):
        self.user_text = None
        self.user_emotion = None
        self.speaker = None

        self.faces = []
        self.objects = []
        self.qr_codes = []

        self.audio_direction = None
        self.last_action = None
        # battery_level persists until overwritten

    def update(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)

    def snapshot(self) -> dict:
        return {
            "user_text": self.user_text,
            "user_emotion": self.user_emotion,
            "speaker": self.speaker,

            "faces": list(self.faces),
            "objects": list(self.objects),
            "qr_codes": list(self.qr_codes),

            "battery_level": self.battery_level,
            "audio_direction": self.audio_direction,
            "last_action": self.last_action,
        }