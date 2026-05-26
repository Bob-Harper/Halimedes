# cortex/context_builder.py

class ContextBuilder:
    """
    Converts raw perception snapshot into higher-level context signals.
    These are NOT decisions — just interpretations of the environment.
    """

    def __init__(self, working_memory):
        self.last_user_presence = False
        self.idle_counter = 0
        self.memory = {}
        self.working_memory = working_memory
        self.world_state = {}
        self.internal_state = {}

    def build(self, perception: dict) -> dict:
        """
        Returns a dict of derived context signals.
        """

        context = {}

        # ------------------------------------------------------------
        # USER PRESENCE
        # ------------------------------------------------------------
        faces = perception.get("faces") or []
        context["user_present"] = len(faces) > 0

        # Track transitions
        if context["user_present"]:
            self.last_user_presence = True
            self.idle_counter = 0
        else:
            self.idle_counter += 1

        context["idle_ticks"] = self.idle_counter

        # ------------------------------------------------------------
        # AUDIO / SPEECH
        # ------------------------------------------------------------
        speaker_text = perception.get("speaker_text")
        context["user_speaking"] = bool(speaker_text)

        # ------------------------------------------------------------
        # ATTENTION TARGET
        # ------------------------------------------------------------
        if faces:
            # Simplest possible: first face
            context["attention_target"] = faces[0]
        else:
            context["attention_target"] = None

        # ------------------------------------------------------------
        # OBSTACLE AWARENESS (ultrasonic)
        # ------------------------------------------------------------
        distance = perception.get("distance_cm")
        if distance is not None:
            try:
                d = float(distance)
                context["obstacle_near"] = d < 20
            except Exception:
                context["obstacle_near"] = False
        else:
            context["obstacle_near"] = False

        return context
