from time import sleep
import asyncio
# the tap tap got broken, it now can't find picrawler?
# legs_list = ['right front', 'left front', 'left rear', 'right rear']
from classes.picrawler import Picrawler  # Robot movement library

class NewMovements():
    def __init__(self, picrawler):
        self.picrawler = picrawler
        self.X_DEFAULT = 45
        self.X_TURN = 70
        self.Y_DEFAULT = 45
        self.Y_START = 0
        self.Z_UP = -30
        self.TURN_X1 = 22.5
        self.TURN_Y1 = 22.5
        self.TURN_X0 = -22.5
        self.TURN_Y0 = -22.5
        self.speed = 50

        # Initialize current positions
        self.current_positions = {
            'x': self.X_DEFAULT,
            'y': self.Y_DEFAULT,
            'z': self.Z_UP
        }

    def update_current_positions(self, steps):
        # Update the current positions based on the last step
        self.current_positions['x'] = steps[-1][0][0]
        self.current_positions['y'] = steps[-1][0][1]
        self.current_positions['z'] = steps[-1][0][2]

    def sit_down(self):
        sit_down_steps = [[50, 90, 90], [50, 90, 90], [50, 90, 90], [50, 90, 90]]
        self.picrawler.do_step(sit_down_steps, speed=1)
        sit_down_steps = [[50, 60, 60], [50, 60, 60], [0, 60, 60], [0, 60, 60]]
        self.picrawler.do_step(sit_down_steps, speed=1)
        sit_down_steps = [[50, 30, 30], [50, 30, 30], [0, 30, 30], [0, 30, 30]]
        self.picrawler.do_step(sit_down_steps, speed=1)
        sit_down_steps = [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]]
        self.picrawler.do_step(sit_down_steps, speed=1)


    def sway_all_legs(self):  # legs_list = ['right front', 'left front', 'left rear', 'right rear']
        tap_front_right = [[45, 45, -44], [45, 45, -30], [45, 45, -30], [45, 45, -30]]
        tap_front_left = [[45, 45, -30], [45, 45, -44], [45, 45, -30], [45, 45, -30]]
        tap_rear_left = [[45, 45, -30], [45, 45, -30], [45, 45, -44], [45, 45, -30]]
        tap_rear_right = [[45, 45, -30], [45, 45, -30], [45, 45, -30], [45, 45, -44]]
        self.picrawler.do_step(tap_front_right, speed=80)
        self.picrawler.do_step(tap_front_left, speed=80)
        self.picrawler.do_step(tap_rear_left, speed=80)
        self.picrawler.do_step(tap_rear_right, speed=80)

    def tap_front_right(self):  # ['right front', 'left front', 'left rear', 'right rear']
        lift_front_right = [[45, 45, 90], [45, 45, -30], [45, 45, -30], [45, 45, -30]]
        tap_front_right = [[45, 45, -40], [45, 45, -30], [45, 45, -30], [45, 45, -30]]
        self.picrawler.do_step(lift_front_right, speed=5)
        self.picrawler.do_step(tap_front_right, speed=99)
        self.picrawler.do_step(lift_front_right, speed=5)
        self.picrawler.do_step(tap_front_right, speed=99)
        self.picrawler.do_step(lift_front_right, speed=5)
        self.picrawler.do_step(tap_front_right, speed=99)

    def tap_front_left(self):  # ['right front', 'left front', 'left rear', 'right rear']
        lift_front_left = [[45, 45, -30], [45, 45, 90], [45, 45, -30], [45, 45, -30]]
        tap_front_left = [[45, 45, -30], [45, 45, -40], [45, 45, -30], [45, 45, -30]]
        self.picrawler.do_step(lift_front_left, speed=5)
        self.picrawler.do_step(tap_front_left, speed=99)
        self.picrawler.do_step(lift_front_left, speed=5)
        self.picrawler.do_step(tap_front_left, speed=99)
        self.picrawler.do_step(lift_front_left, speed=5)
        self.picrawler.do_step(tap_front_left, speed=99)

    def tap_rear_right(self):  # ['right front', 'left front', 'left rear', 'right rear']
        lift_rear_right = [[45, 45, -30], [45, 45, -30], [45, 45, -30], [45, 45, 90]]
        tap_rear_right = [[45, 45, -30], [45, 45, -30], [45, 45, -30], [45, 45, -40]]
        self.picrawler.do_step(lift_rear_right, speed=5)
        self.picrawler.do_step(tap_rear_right, speed=99)
        self.picrawler.do_step(lift_rear_right, speed=5)
        self.picrawler.do_step(tap_rear_right, speed=99)
        self.picrawler.do_step(lift_rear_right, speed=5)
        self.picrawler.do_step(tap_rear_right, speed=99)

    def tap_rear_left(self):  # ['right front', 'left front', 'left rear', 'right rear']
        lift_rear_left = [[45, 45, -30], [45, 45, -30], [45, 45, 90], [45, 45, -30]]
        tap_rear_left = [[45, 45, -30], [45, 45, -30], [45, 45, -40], [45, 45, -30]]
        self.picrawler.do_step(lift_rear_left, speed=5)
        self.picrawler.do_step(tap_rear_left, speed=99)
        self.picrawler.do_step(lift_rear_left, speed=5)
        self.picrawler.do_step(tap_rear_left, speed=99)
        self.picrawler.do_step(lift_rear_left, speed=5)
        self.picrawler.do_step(tap_rear_left, speed=99)

    def tap_all_legs(self):
        lift_front_right = [[45, 45, 90], [45, 45, -30], [45, 45, -30], [45, 45, -30]]
        tap_front_right = [[45, 45, -40], [45, 45, -30], [45, 45, -30], [45, 45, -30]]
        lift_front_left = [[45, 45, -30], [45, 45, 90], [45, 45, -30], [45, 45, -30]]
        tap_front_left = [[45, 45, -30], [45, 45, -40], [45, 45, -30], [45, 45, -30]]
        lift_rear_right = [[45, 45, -30], [45, 45, -30], [45, 45, -30], [45, 45, 90]]
        tap_rear_right = [[45, 45, -30], [45, 45, -30], [45, 45, -30], [45, 45, -40]]
        lift_rear_left = [[45, 45, -30], [45, 45, -30], [45, 45, 90], [45, 45, -30]]
        tap_rear_left = [[45, 45, -30], [45, 45, -30], [45, 45, -40], [45, 45, -30]]

        self.picrawler.do_step(lift_front_right, speed=25)
        self.picrawler.do_step(tap_front_right, speed=99)
        self.picrawler.do_step(lift_front_left, speed=25)
        self.picrawler.do_step(tap_front_left, speed=99)
        self.picrawler.do_step(lift_rear_left, speed=25)
        self.picrawler.do_step(tap_rear_left, speed=99)
        self.picrawler.do_step(lift_rear_right, speed=25)
        self.picrawler.do_step(tap_rear_right, speed=99)


    def point(self):  # ['right front', 'left front', 'left rear', 'right rear']
        return [
            [[self.X_DEFAULT, self.Y_DEFAULT, self.z_current],[self.X_TURN, self.Y_START,self.Z_UP],[self.X_DEFAULT, self.Y_START, self.z_current],[self.X_DEFAULT, self.Y_DEFAULT, self.z_current]],
            [[self.X_DEFAULT, self.Y_DEFAULT, self.z_current],[self.X_START, self.Y_WAVE,self.Z_WAVE],[self.X_DEFAULT, self.Y_START, self.z_current],[self.X_DEFAULT, self.Y_DEFAULT, self.z_current]],
            [[self.X_DEFAULT, self.Y_DEFAULT, self.z_current],[self.X_START, self.Y_WAVE,self.Z_UP],[self.X_DEFAULT, self.Y_START, self.z_current],[self.X_DEFAULT, self.Y_DEFAULT, self.z_current]],
            [[self.X_DEFAULT, self.Y_DEFAULT, self.z_current],[self.X_START, self.Y_WAVE,self.Z_WAVE],[self.X_DEFAULT, self.Y_START, self.z_current],[self.X_DEFAULT, self.Y_DEFAULT, self.z_current]],
            [[self.X_DEFAULT, self.Y_DEFAULT, self.z_current],[self.X_START, self.Y_WAVE,self.Z_UP],[self.X_DEFAULT, self.Y_START, self.z_current],[self.X_DEFAULT, self.Y_DEFAULT, self.z_current]],
            [[self.X_DEFAULT, self.Y_DEFAULT, self.z_current],[self.X_START, self.Y_WAVE,self.Z_WAVE],[self.X_DEFAULT, self.Y_START, self.z_current],[self.X_DEFAULT, self.Y_DEFAULT, self.z_current]],
            [[self.X_DEFAULT, self.Y_DEFAULT, self.z_current],[self.X_START, self.Y_WAVE,self.Z_UP],[self.X_DEFAULT, self.Y_START, self.z_current],[self.X_DEFAULT, self.Y_DEFAULT, self.z_current]],

            [[self.X_DEFAULT, self.Y_DEFAULT, self.z_current],[self.X_TURN, self.Y_START,self.Z_UP],[self.X_DEFAULT, self.Y_START, self.z_current],[self.X_DEFAULT, self.Y_DEFAULT, self.z_current]],
            [[self.X_DEFAULT, self.Y_DEFAULT, self.z_current],[self.X_DEFAULT, self.Y_START,self.z_current],[self.X_DEFAULT, self.Y_START, self.z_current],[self.X_DEFAULT, self.Y_DEFAULT, self.z_current]],
        ]

    def stand_tall(self):
        stand_tall_steps = [[45, 45, -90], [45, 45, -90], [45, 45, -90], [45, 45, -90]]
        self.picrawler.do_step(stand_tall_steps, speed=50)

    def small_right(self):
        # Define all positions upfront
        stand_tall_steps = [[45, 45, -90], [45, 45, -90], [45, 45, -90], [45, 45, -90]]
        step1 = [[45, 45, -90], [75, 30, -60], [45, 45, -90], [45, 45, -90]]  # Front right lifts outward
        step2 = [[45, 45, -90], [75, 30, -90], [45, 45, -90], [45, 45, -90]]  # Front right taps down
        step3 = [[15, 30, -60], [75, 30, -90], [45, 45, -90], [45, 45, -90]]  # Front left lifts inward
        step4 = [[15, 30, -90], [75, 30, -90], [45, 45, -90], [45, 45, -90]]  # Front left taps down
        step5 = [[15, 30, -90], [75, 30, -90], [25, 30, -60], [45, 45, -90]]  # Rear left adjusts inward
        step6 = [[15, 30, -90], [75, 30, -90], [25, 30, -90], [45, 45, -90]]  # Rear left taps down
        step7 = [[15, 30, -90], [75, 30, -90], [25, 30, -90], [65, 30, -60]]  # Rear right adjusts outward
        step8 = [[15, 30, -90], [75, 30, -90], [25, 30, -90], [65, 30, -90]]  # Rear right taps down

        # Execute the steps in sequence
        self.picrawler.do_step(stand_tall_steps, speed=50)
        self.picrawler.do_step(step1, speed=25)
        self.picrawler.do_step(step2, speed=99)
        self.picrawler.do_step(step3, speed=25)
        self.picrawler.do_step(step4, speed=99)
        self.picrawler.do_step(step5, speed=25)
        self.picrawler.do_step(step6, speed=99)
        self.picrawler.do_step(step7, speed=25)
        self.picrawler.do_step(step8, speed=99)


    async def sit_down_async(self):

        sit_down_steps = [
            [[50, 90, 90], [50, 90, 90], [50, 90, 90], [50, 90, 90]],
            [[50, 60, 60], [50, 60, 60], [0, 60, 60], [0, 60, 60]],
            [[50, 30, 30], [50, 30, 30], [0, 30, 30], [0, 30, 30]],
            [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]]
        ]
        for steps in sit_down_steps:
            await asyncio.to_thread(self.picrawler.do_step, steps, speed=1)

    async def sway_all_legs_async(self):
        tap_steps = [
            [[45, 45, -44], [45, 45, -30], [45, 45, -30], [45, 45, -30]],
            [[45, 45, -30], [45, 45, -44], [45, 45, -30], [45, 45, -30]],
            [[45, 45, -30], [45, 45, -30], [45, 45, -44], [45, 45, -30]],
            [[45, 45, -30], [45, 45, -30], [45, 45, -30], [45, 45, -44]]
        ]
        for steps in tap_steps:
            await asyncio.to_thread(self.picrawler.do_step, steps, speed=80)

    async def tap_front_right_async(self):
        lift_front_right = [[45, 45, 90], [45, 45, -30], [45, 45, -30], [45, 45, -30]]
        tap_front_right = [[45, 45, -40], [45, 45, -30], [45, 45, -30], [45, 45, -30]]
        for _ in range(3):
            await asyncio.to_thread(self.picrawler.do_step, lift_front_right, speed=5)
            await asyncio.to_thread(self.picrawler.do_step, tap_front_right, speed=99)

    async def tap_all_legs_async(self):
        steps = [
            [[45, 45, 90], [45, 45, -30], [45, 45, -30], [45, 45, -30]],
            [[45, 45, -40], [45, 45, -30], [45, 45, -30], [45, 45, -30]],
            [[45, 45, -30], [45, 45, 90], [45, 45, -30], [45, 45, -30]],
            [[45, 45, -30], [45, 45, -40], [45, 45, -30], [45, 45, -30]],
            [[45, 45, -30], [45, 45, -30], [45, 45, -30], [45, 45, 90]],
            [[45, 45, -30], [45, 45, -30], [45, 45, -30], [45, 45, -40]],
            [[45, 45, -30], [45, 45, -30], [45, 45, 90], [45, 45, -30]],
            [[45, 45, -30], [45, 45, -30], [45, 45, -40], [45, 45, -30]]
        ]
        for step in steps:
            await asyncio.to_thread(self.picrawler.do_step, step, speed=25)
            await asyncio.to_thread(self.picrawler.do_step, step, speed=99)

    async def stand_tall_async(self):
        stand_tall_steps = [[45, 45, -90], [45, 45, -90], [45, 45, -90], [45, 45, -90]]
        await asyncio.to_thread(self.picrawler.do_step, stand_tall_steps, speed=50)
