# body/locomotion_manager.py

class LocomotionManager:
    def __init__(self, picrawler):
        self.picrawler = picrawler

    async def stop(self):
        # Picrawler stop is synchronous, but wrap for consistency
        self.picrawler.stop()

    async def step_back(self):
        await self.picrawler.backward(1)

    async def back_up(self):
        await self.picrawler.backward(2)

    async def turn_away_left(self):
        await self.picrawler.turn_left(1)

    async def turn_away_right(self):
        await self.picrawler.turn_right(1)

    async def turn_angle_left(self, angle=15):
        await self.picrawler.turn_left_angle(1, angle=angle)

    async def turn_angle_right(self, angle=15):
        await self.picrawler.turn_right_angle(1, angle=angle)

    async def recover_posture(self):
        await self.picrawler.stand(1)

    async def brace(self):
        # temporary until we define a real brace pose
        await self.picrawler.stand_tall()

    async def investigate_forward(self):
        await self.picrawler.forward(1)

    async def investigate_backward(self):
        await self.picrawler.backward(1)

    async def look_left(self):
        await self.picrawler.look_left(1)

    async def look_right(self):
        await self.picrawler.look_right(1)

    async def look_down(self):
        await self.picrawler.look_down(1)

    async def look_up(self):
        await self.picrawler.look_up(1)

    async def glance_left(self):
        await self.picrawler.glance(direction="left", angle=25)

    async def glance_right(self):
        await self.picrawler.glance(direction="right", angle=25)

    async def glance_forward(self):
        await self.picrawler.glance(direction="forward", angle=25)
