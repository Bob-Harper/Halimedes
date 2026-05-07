class PerceptionManager:
    def __init__(self, hardware_state, emotion_categorizer, vision):
        self.hardware_state = hardware_state
        self.emotion_categorizer = emotion_categorizer
        self.vision = vision

        for k, v in self.FIELDS.items():
            setattr(self, k, v if not isinstance(v, list) else [])

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

    def ingest_audio_event(self, spoken_text, speaker, transcription, truncated):
        self.speaker_text = spoken_text
        self.speaker = speaker

        # compute emotion internally
        self.speaker_emotion = self.emotion_categorizer.analyze_text_emotion(spoken_text)

        # transcription metadata
        self.speech_confidence = transcription.get("confidence")
        self.utterance_duration = transcription.get("duration")
        self.truncated = truncated

        # hardware + vision
        self.hardware_status = self.hardware_state.snapshot()
        self.faces = self.vision.get_faces()
        self.objects = self.vision.get_objects()
        self.qr_codes = self.vision.get_qr_codes()
