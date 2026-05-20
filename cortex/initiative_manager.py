# cortex/initiative_manager.py

class InitiativeManager:
    """
    Determines whether Hal should initiate a behavior on his own.
    Produces a suggested IntentType or None.
    """

    def __init__(self):
        self.idle_threshold = 50       # ticks of no user interaction
        self.explore_threshold = 200   # long idle → explore
        self.last_user_interaction = 0
        self.last_action = 0

    def tick(self):
        """Called once per cognition loop."""
        self.last_user_interaction += 1
        self.last_action += 1

    def suggest(self, perception, world_state, internal_state):

        # USER SPOKE
        if perception["speaker_text"]:
            self.last_user_interaction = 0
            return None

        # NEW FACE APPEARED
        if perception["faces"] and self._is_new_face(perception, world_state):
            return "greet"

        # LONG IDLE
        if self.last_user_interaction > self.idle_threshold:
            return "idle"

        # VERY LONG IDLE
        if self.last_user_interaction > self.explore_threshold:
            return "explore"

        # BORED
        if internal_state.activity_level < 0.3 and self.last_action > 30:
            return "look_around"

        return None


    def _is_new_face(self, perception, world_state):
        return len(perception["faces"]) > len(world_state.faces)

