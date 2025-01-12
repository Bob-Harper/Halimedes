import random
from classes.picrawler import Picrawler
from classes.new_movements import NewMovements

class PassiveActionsManager:
    def __init__(self):
        self.crawler = Picrawler()
        self.newmovements = NewMovements(self.crawler)

    async def actions_thinking(self):
        """Perform a random thinking action."""
        action = random.choice([
            self.newmovements.tap_front_right_async,
            self.newmovements.tap_front_left_async,
            self.newmovements.tap_rear_right_async,
            self.newmovements.tap_rear_left_async,
            self.newmovements.tap_all_legs_async,
        ])
        await action()  # Directly execute the chosen action


