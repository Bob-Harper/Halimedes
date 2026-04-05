# body/locomotion_manager.py

class LocomotionManager:
    def __init__(self, picrawler):
        self.picrawler = picrawler

    async def look_toward_sound(self):
        # Use your existing sound localization if available
        # or just rotate a bit for now
        await self.picrawler.turn_random_direction()

    async def move_toward(self, direction):
        await self.picrawler.step(direction)

    async def follow_user(self, identity):
        # Placeholder for future behavior
        pass

    async def explore(self):
        # Placeholder for autonomous wandering
        pass