class WorldStateManager:
    def __init__(self):
        self.location = "unknown"
        self.objects = []
        self.faces = []
        self.time_of_day = "unknown"
        self.lighting = "unknown"

    def update(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)

    def snapshot(self) -> dict:
        return {
            "location": self.location,
            "objects": list(self.objects),
            "faces": list(self.faces),
            "time_of_day": self.time_of_day,
            "lighting": self.lighting
        }