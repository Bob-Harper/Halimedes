import datetime

class WorldStateManager:
    def __init__(self):
        self.location = "unknown"
        self.objects = []
        self.faces = []
        self.time_of_day = "unknown"
        self.lighting = "unknown"
        self.events = []

    def update(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)

    def add_event(self, event: dict):
        self.events.append(event)

    def add_face(self, face):
        self.faces.append(face)

    def add_object(self, obj):
        self.objects.append(obj)

    def snapshot(self) -> dict:
        return {
            "location": self.location,
            "objects": list(self.objects),
            "faces": list(self.faces),
            "time_of_day": self.get_time_of_day(),
            "lighting": self.lighting,
            "events": list(self.events)
        }

    def get_time_of_day(self):
        time = datetime.datetime.now().time()
        if time >= datetime.time(6, 0) and time < datetime.time(12, 0):
            return "morning"
        elif time >= datetime.time(12, 0) and time < datetime.time(18, 0):
            return "afternoon"
        elif time >= datetime.time(18, 0) and time < datetime.time(22, 0):
            return "evening"
        else:
            return "night"
