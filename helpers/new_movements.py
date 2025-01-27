from time import sleep
import asyncio
# the tap tap got broken, it now can't find picrawler?
# legs_list = ['right front', 'left front', 'left rear', 'right rear']
# from classes.picrawler import Picrawler  # passing in so dont need to import right now

class NewMovements():
    def __init__(self, crawler):
        self.picrawler = crawler
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

    def prepare_to_twist(self):
        prepare_to_twist = [[90, 10, -60], [90, 10, -60], [25, 65, -60], [25, 65, -60]]
        self.picrawler.do_step(prepare_to_twist, speed=50)    

    def pushup(self, speed):
        up=[[80, 0, -100], [80, 0, -100],[0, 120, -60], [0, 120, -60]]
        down=[[80, 0, -30], [80, 0, -30],[0, 120, -60], [0, 120, -60]]
        self.picrawler.do_step(up,speed)
        sleep(0.6)
        self.picrawler.do_step(down,speed)
        sleep(0.6)

    def swimming(self, speed):
        for i in range(100):
            self.picrawler.do_step([[100-i,i,0],[100-i,i,0],[0,120,-60+i/5],[0,100,-40-i/5]],speed)

    def handwork(self, speed):

        basic_step = []
        basic_step = self.picrawler.step_list.get("sit")
        left_hand  = self.picrawler.mix_step(basic_step,0,[0,50,80])
        right_hand  = self.picrawler.mix_step(basic_step,1,[0,50,80])
        two_hand = self.picrawler.mix_step(left_hand,1,[0,50,80])

        self.picrawler.do_step('sit',speed)
        sleep(0.6)    
        self.picrawler.do_step(left_hand,speed)
        sleep(0.6)
        self.picrawler.do_step(two_hand,speed)
        sleep(0.6)
        self.picrawler.do_step(right_hand,speed)
        sleep(0.6)
        self.picrawler.do_step('sit',speed)
        sleep(0.6)
 
    async def wiggle(self):
        """Perform a smooth wiggle motion."""
        new_step = [[50, 50, -80], [50, 50, -80], [50, 50, -80], [50, 50, -80]]
        speed = 99

        while True:  # Continuous loop, can be broken externally if needed
            for i in range(4):  # Cycle through legs
                for inc in range(30, 60, 80):  # Increment rise/drop values
                    rise = [50, 50, (-80 + inc * 0.5)]
                    drop = [50, 50, (-80 - inc)]
                    new_step[i] = rise
                    new_step[(i + 2) % 4] = drop
                    new_step[(i + 1) % 4] = rise
                    new_step[(i - 1) % 4] = drop
                    await asyncio.to_thread(self.picrawler.do_step, new_step, speed)
                    await asyncio.sleep(0.05)  # Small delay for smoother animation    

    async def glance(self, direction="center", angle=30, speed=99):
        """
        Perform a smooth glance motion in the specified direction.
        
        Parameters:
            direction (str): "left", "right", or "center".
            angle (int): The angle to turn for glancing.
            speed (int): Speed of the movement.
        """
        print(f"Glancing {direction} at {angle} degrees.")
        
        # Define the base position (stable, elevated posture)
        base_position = [[90, 10, -60], [90, 10, -60], [25, 65, -60], [25, 65, -60]]

        # Define a slightly lifted position to maintain stability during the twist
        lifted_position = [[90, 10, -50], [90, 10, -50], [25, 65, -50], [25, 65, -50]]

        # Adjust positions based on the direction
        if direction == "left":
            # Exaggerate twist left with lift
            glance_position = [
                [90 - angle, 10 + angle, -50],  # Left front twists inward
                [90 + angle, 10 - angle, -70],  # Right front twists outward
                [25 - angle, 65 + angle, -50],  # Left rear twists inward
                [25 + angle, 65 - angle, -70],  # Right rear twists outward
            ]
        elif direction == "right":
            # Exaggerate twist right with lift
            glance_position = [
                [90 + angle, 10 - angle, -50],  # Left front twists outward
                [90 - angle, 10 + angle, -70],  # Right front twists inward
                [25 + angle, 65 - angle, -50],  # Left rear twists outward
                [25 - angle, 65 + angle, -70],  # Right rear twists inward
            ]
        else:
            # Reset to base position
            glance_position = base_position

        # Perform the glance motion
        print("Lifting body for stability...")
        await asyncio.to_thread(self.picrawler.do_step, lifted_position, speed)  # Transition to lifted position
        await asyncio.sleep(0.3)

        print(f"Twisting {direction}...")
        await asyncio.to_thread(self.picrawler.do_step, glance_position, speed)  # Execute the twist
        await asyncio.sleep(0.5)

        print("Resetting to base position...")
        await asyncio.to_thread(self.picrawler.do_step, base_position, speed)  # Reset to base position
        await asyncio.sleep(0.3)
