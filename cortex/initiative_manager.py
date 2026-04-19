# cortex/initiative_manager.py

class InitiativeManager:
    """
    Determines whether Hal should initiate a behavior on his own.
    Produces a suggested IntentType or None.
    """

    def __init__(self):
        self.idle_threshold = 50      # ticks
        self.explore_threshold = 200  # ticks

    def suggest(self, context: dict, internal_state) -> str | None:
        """
        Returns one of:
            "idle"
            "explore"
            "greet"
            None  (no initiative)
        """

        # ------------------------------------------------------------
        # USER PRESENCE → greet
        # ------------------------------------------------------------
        if context.get("user_present") and internal_state.current_activity == "idle":
            return "greet"

        # ------------------------------------------------------------
        # LONG IDLE → idle animation
        # ------------------------------------------------------------
        if context.get("idle_ticks", 0) > self.idle_threshold:
            return "idle"

        # ------------------------------------------------------------
        # VERY LONG IDLE → explore
        # ------------------------------------------------------------
        if context.get("idle_ticks", 0) > self.explore_threshold:
            return "explore"

        return None
