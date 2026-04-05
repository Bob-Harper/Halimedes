# mind/decision_manager.py

from enum import Enum, auto
import time

class Intent(Enum):
    IDLE = auto()
    RESPOND_TO_USER = auto()
    GREET_USER = auto()
    INVESTIGATE_SOUND = auto()
    SEEK_INFORMATION = auto()
    EXPRESS_EMOTION = auto()
    PERFORM_IDLE_BEHAVIOR = auto()
    INTERRUPT = auto()

class DecisionManager:
    def __init__(self):
        self.current_intent = Intent.IDLE
        self.last_user = None
        self.last_interaction_time = 0

        # Hal’s internal state — this will evolve over time
        self.internal_state = {
            "mood": "neutral",
            "energy": 0.7,
            "curiosity": 0.5,
            "boredom": 0.0,
            "engaged": False
        }

        # Future expansion: goal stack
        self.goals = []

    def update_internal_state(self, event_type):
        if event_type == "speech":
            self.internal_state["boredom"] = 0
            self.internal_state["engaged"] = True

        elif event_type == "silence":
            self.internal_state["boredom"] += 0.1
            self.internal_state["engaged"] = False

        elif event_type == "face":
            self.internal_state["curiosity"] += 0.1

    def decide(self, sensory_event):
        """
        sensory_event example:
        {
            "type": "speech" | "face" | "noise" | "silence" | "llm_response",
            "data": {...}
        }
        """

        event_type = sensory_event["type"]
        self.update_internal_state(event_type)

        # 1. User speech always takes priority
        if event_type == "speech":
            self.last_interaction_time = time.time()
            self.current_intent = Intent.RESPOND_TO_USER
            return self.current_intent

        # 2. Face recognition event
        if event_type == "face":
            identity = sensory_event["data"].get("identity")
            if identity and identity != self.last_user:
                self.last_user = identity
                self.current_intent = Intent.GREET_USER
                return self.current_intent

        # 3. Noise without speech
        if event_type == "noise":
            self.current_intent = Intent.INVESTIGATE_SOUND
            return self.current_intent

        # 4. Idle behavior when bored
        if self.internal_state["boredom"] > 0.5:
            self.current_intent = Intent.PERFORM_IDLE_BEHAVIOR
            return self.current_intent

        # 5. Default fallback
        self.current_intent = Intent.IDLE
        return self.current_intent