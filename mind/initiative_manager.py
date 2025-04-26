import random
import time


class InitiativeManager:
    def __init__(self):
        self.last_interaction = time.time()

    def register_interaction(self):
        self.last_interaction = time.time()

    def should_initiate_action(self):
        return (time.time() - self.last_interaction) > random.randint(300, 600)  # 5-10 minutes idle
