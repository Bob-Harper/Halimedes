class BehaviorPlan:
    """
    Unified plan object consumed by BehaviorExecutor.
    """

    def __init__(self):
        self.should_interrupt = False

        self.speech = {
            "output_speech": []
        }

        self.nonverbal = {
            "gaze": [],        # list[{"mode": str, "when": str}]
            "expression": [],  # list[{"mood": str, "when": str}]
            "sounds": [],      # list[{"category": str, "when": str}]
        }

        # list[{"category": str, "type": str, ...}]
        self.actions = []

        self.memory = {
            "write": []
        }

        self.world_state = {
            "update": []
        }
