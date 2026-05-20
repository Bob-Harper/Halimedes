import random
import math

class DecisionPolicy:
    """
    Entry point for HAL's future ANN policy network.
    Takes a state vector and returns a BEHAVIOR string.
    """

    def __init__(self):
        # Temporary behavior weights (will be replaced by ANN outputs)
        self.behavior_weights = {
            "converse": 1.0,
            "act": 0.5,
            "observe": 1.0,
            "idle": 1.0,
            "idle_fidget": 0.3,
            "internal": 0.3,
            "greet": 0.2,
            "explore": 0.0,   # disabled for safety
        }

    def decide(self, state_vector):
        """
        Convert weights → probabilities → sample a behavior.
        ANN will replace this.
        """

        items = list(self.behavior_weights.items())

        logits = [w for _, w in items]
        max_logit = max(logits)
        exp = [math.exp(l - max_logit) for l in logits]
        total = sum(exp)
        probs = [e / total for e in exp]

        r = random.random()
        cumulative = 0.0
        for (behavior, _), p in zip(items, probs):
            cumulative += p
            if r <= cumulative:
                return behavior

        return "observe"
