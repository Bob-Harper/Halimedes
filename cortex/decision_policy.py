import random
import math

class DecisionPolicy:
    """
    Hal's proto-cortex.
    Takes a state vector (dict of floats) and returns an intent string.
    This version uses a simple weighted sampler so you can test the pipeline.
    Later, replace with an ANN.
    """

    def __init__(self):
        # Temporary weights for each intent.
        # These will eventually be learned by the ANN.
        self.intent_weights = {
            "converse": 1.0,
            "act": 0.5,
            "ignore": 0.2,
            "observe": 1.0,
            "command": 0.5,
            "explore": 0.8,
            "idle": 1.0,
            "internal": 0.3,
        }

    def decide(self, state_vector):
        """
        Convert weights → probabilities → sample an intent.
        """

        # Convert weights to a list of (intent, weight)
        items = list(self.intent_weights.items())

        # Softmax to get probabilities
        logits = [w for _, w in items]
        max_logit = max(logits)
        exp = [math.exp(l - max_logit) for l in logits]
        total = sum(exp)
        probs = [e / total for e in exp]

        # Sample
        r = random.random()
        cumulative = 0.0
        for (intent, _), p in zip(items, probs):
            cumulative += p
            if r <= cumulative:
                return intent

        # Fallback
        return "observe"
