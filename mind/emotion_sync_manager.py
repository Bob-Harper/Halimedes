# import stuff


class EmotionSyncManager:
    def __init__(self, emotion_engine, eye_controller, voice_controller):
        self.emotion_engine = emotion_engine
        self.eye_controller = eye_controller
        self.voice_controller = voice_controller

    def sync_all(self):
        mood = self.emotion_engine.get_emotion()

        # Eye expression sync
        self.eye_controller.set_expression_by_mood(mood)

        # Voice cadence sync
        pitch, speed = self.map_mood_to_voice(mood)
        self.voice_controller.set_voice_modifiers(pitch, speed)

    def map_mood_to_voice(self, mood):
        voice_map = {
            "happy": (1.3, 0.8),
            "neutral": (1.0, 1.0),
            "sad": (0.6, 1.2),
            "angry": (0.5, 1.15),
            "curious": (1.25, 0.9),
            "sleepy": (0.75, 1.25),
            "cautious": (0.85, 1.1)
        }
        return voice_map.get(mood, (1.0, 1.0))  # fallback
