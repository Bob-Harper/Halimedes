class PerceptionManager:
    def __init__(self):
        self.user_text = ""
        self.speaker = "unknown"
        self.user_emotion = "neutral"
        self.faces_detected = []
        self.objects_detected = []
        self.audio_energy = 0.0

    def reset(self):
        self.user_text = ""
        self.speaker = "unknown"
        self.user_emotion = "neutral"
        self.faces_detected = []
        self.objects_detected = []
        self.audio_energy = 0.0

    def update(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)

    def snapshot(self) -> dict:
        return {
            "user_text": self.user_text,
            "speaker": self.speaker,
            "user_emotion": self.user_emotion,
            "faces_detected": list(self.faces_detected),
            "objects_detected": list(self.objects_detected),
            "audio_energy": self.audio_energy
        }