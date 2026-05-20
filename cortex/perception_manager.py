class PerceptionManager:
    def __init__(
        self,
        hardware_state,
        sensor_state,
        emotion_categorizer,
        vision
    ):
        self.hardware_state = hardware_state
        self.sensor_state = sensor_state
        self.emotion_categorizer = emotion_categorizer
        self.vision = vision

        for k, v in self.FIELDS.items():
            setattr(self, k, v if not isinstance(v, list) else [])

    FIELDS = {
        # Microphone
        "speaker_text": None,
        "speaker_emotion": None,
        "speaker": None,
        "audio_direction": None,
        "speech_confidence": None,
        "utterance_duration": None,
        "truncated": False,

        # Camera
        "faces": [],
        "objects": [],
        "qr_codes": [],

        # Pi readings
        "hardware_status": {},

        # Self
        "last_action": None,

        # ISensors
        "sensor_status": {},

        # --- NEW FIELDS replacing server intent ---
        "intent": None,
        "behavior": None,
        "speech": [],
        "nonverbal_output_speech": {},
        "memory_updates": [],
        "world_updates": [],
        "actions": [],
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
        self.sensor_status = self.sensor_state.snapshot()
        self.faces = self.vision.get_faces()
        self.objects = self.vision.get_objects()
        self.qr_codes = self.vision.get_qr_codes()

    def update_from_vision(self):
        if self.vision:
            try:
                faces = self.vision.get_faces()
                if faces is not None:
                    self.faces = faces

                objects = self.vision.get_objects()
                if objects is not None:
                    self.objects = objects

                qr = self.vision.get_qr_codes()
                if qr is not None:
                    self.qr_codes = qr

            except Exception as e:
                print(f"[Perception] Vision update failed: {e}")

