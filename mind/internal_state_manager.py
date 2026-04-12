class InternalStateManager:
    def __init__(self):
        self.energy = 1.0
        self.boredom = 0.0
        self.curiosity = 0.5
        self.confidence = 0.5
        self.emotion = "neutral"

    def update(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)

    def snapshot(self) -> dict:
        return {
            "energy": self.energy,
            "boredom": self.boredom,
            "curiosity": self.curiosity,
            "confidence": self.confidence,
            "emotion": self.emotion
        }