# body/locomotion_manager.py

class LocomotionManager:
    def __init__(self, picrawler, picrawler_extended):
        self.picrawler = picrawler
        self.ext = picrawler_extended

        self.speed_default = 100
        self.speed_turbo = 200
        self.speed = self.speed_default

    def _do(self, target, motion_name, step=1, speed=None, **kwargs):
        if speed is None:
            speed = self.speed

        if target == "ext":
            method = getattr(self.ext, motion_name)
            return method(**kwargs) if kwargs else method()

        return self.picrawler.do_action(motion_name, step, speed, **kwargs)

    #
    # existing locomotion primitives named to make it easier to match to sensor reflexes and decision making paths..
    #
    def stop(self):
        self.picrawler.stop()

    def step_back(self):
        self._do("pic", "backward", step=1)

    def back_up(self):
        self._do("pic", "backward", step=2)

    def turn_away_left(self):
        self._do("pic", "turn left", step=1)

    def turn_away_right(self):
        self._do("pic", "turn right", step=1)

    def turn_angle_left(self, angle=15):
        self._do("pic", "turn left angle", step=1, angle=angle)

    def turn_angle_right(self, angle=15):
        self._do("pic", "turn right angle", step=1, angle=angle)

    def recover_posture(self):
        self._do("pic", "stand", step=1)

    def brace(self):
        self.ext.stand_tall()

    def investigate_forward(self):
        self._do("pic", "forward", step=1)

    def investigate_backward(self):
        self._do("pic", "backward", step=1)

    #
    # head / glance / look
    #
    def look_left(self):
        self._do("pic", "look left", step=1)

    def look_right(self):
        self._do("pic", "look right", step=1)

    def look_down(self):
        self._do("pic", "look down", step=1)

    def look_up(self):
        self._do("pic", "look up", step=1)

    def glance_left(self):
        return self.ext.glance(direction="left", angle=25, speed=self.speed)

    def glance_right(self):
        return self.ext.glance(direction="right", angle=25, speed=self.speed)

    def glance_forward(self):
        return self.ext.glance(direction="forward", angle=25, speed=self.speed)

    #
    # NEW: movements created from keyboard controller for future calls
    #
    def sit(self):
        self._do("pic", "sit", step=1)

    def stand(self):
        self._do("pic", "stand", step=1)

    def wave(self):
        self._do("pic", "wave", step=1)

    def swimming(self, count=3):
        return self.ext.swimming(count=count, speed=self.speed)

    def pushup(self, count=3):
        return self.ext.pushup(count, speed=self.speed)

    def twist(self):
        return self.ext.twist(speed=self.speed)

    def handwork(self):
        return self.ext.handwork(speed=self.speed)

    def tap_front_right(self):
        return self.ext.tap_front_right()

    def tap_front_left(self):
        return self.ext.tap_front_left()

    def tap_rear_right(self):
        return self.ext.tap_rear_right()

    def tap_rear_left(self):
        return self.ext.tap_rear_left()

    def stand_tall(self):
        return self.ext.stand_tall()

    def stretch_out(self):
        return self.ext.stretch_out()

    async def wiggle(self):
        return await self.ext.wiggle()

    async def glance_left_forward(self):
        await self.ext.glance(direction="left", angle=25, speed=self.speed)
        await self.ext.glance(direction="forward", angle=25, speed=self.speed)

    async def glance_right_forward(self):
        await self.ext.glance(direction="right", angle=25, speed=self.speed)
        await self.ext.glance(direction="forward", angle=25, speed=self.speed)

    async def glance_left_forward_right_forward(self):
        await self.ext.glance(direction="left", angle=25, speed=self.speed)
        await self.ext.glance(direction="forward", angle=25, speed=self.speed)
        await self.ext.glance(direction="right", angle=25, speed=self.speed)
        await self.ext.glance(direction="forward", angle=25, speed=self.speed)

    def sit_down(self): # a more articulated shutdown version of Sit Down
        return self.ext.sit_down()

    def sway_all_legs(self):
        return self.ext.sway_all_legs()

    def tap_all_legs(self): # all 4 legs on rotation
        return self.ext.tap_all_legs()

    async def run_wiggle_for_seconds(self, duration=3):  # Wiggle but ith a timer
        return await self.ext.run_wiggle_for_seconds(duration)

    async def glance(self, direction="center", angle=30): # twist body up and slightly then return to center
        return await self.ext.glance(direction=direction,
                                     angle=angle,
                                     speed=self.speed)

    def wave_leg(self, leg='rf'): # leg_mapping = {'rf': 0, 'lf': 1, 'lr': 2, 'rr': 3}
        return self.ext.wave(speed=self.speed, leg=leg)
