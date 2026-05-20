class InternalStateManager:
    """
    HAL's internal brain state.
    Single source of truth for drives, mood, and continuity.
    """

    def __init__(self):
        # Drives
        self.energy = 1.0
        self.boredom = 0.0
        self.curiosity = 0.5
        self.confidence = 0.5
        self.emotion = "neutral"
        self.activity_level = 1.0

        # Conversational continuity
        self.last_user_text = None
        self.last_user_emotion = None
        self.last_speaker = None
        self.conversation_turns = 0

        # Short-term memory (rolling window)
        self.short_term_memory = []  # list[dict]

        # Emotional carryover
        self.mood = "neutral"
        self.arousal = 0.0

        # Speech state
        self.is_speaking = False
        self.pending_speech = []
        self.pending_speech_priority = 0
        self.current_speech_priority = 0

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
            "emotion": self.emotion,
            "mood": self.mood,
            "arousal": self.arousal,
            "last_user_text": self.last_user_text,
            "last_user_emotion": self.last_user_emotion,
            "last_speaker": self.last_speaker,
            "conversation_turns": self.conversation_turns,
            "short_term_memory": list(self.short_term_memory),
        }
