class PerceptionManager:
    FIELDS = {
        "speaker_text": None,
        "speaker_emotion": None,
        "speaker": None,

        "faces": [],
        "objects": [],
        "qr_codes": [],

        "hardware_status": {},

        "audio_direction": None,
        "last_action": None,

        "speech_confidence": None,
        "utterance_duration": None,
        "truncated": False,
    }

    def __init__(self):
        for k, v in self.FIELDS.items():
            setattr(self, k, v if not isinstance(v, list) else [])

    def reset(self):
        for k, v in self.FIELDS.items():
            if k == "hardware_status":
                continue  # <-- DO NOT RESET HARDWARE
            setattr(self, k, v if not isinstance(v, list) else [])


    def update(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)

    def snapshot(self) -> dict:
        return {k: getattr(self, k) for k in self.FIELDS}
