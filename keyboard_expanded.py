from helpers.picrawler import Picrawler
from time import sleep
import readchar
import asyncio
from helpers.new_movements import NewMovements


class RobotKeyboard:
    def __init__(self):
        self.speed = 99
        self.picrawler = Picrawler()
        self.new_movements = NewMovements(self.picrawler)
        self.manual = '''
        Press keys on keyboard to control PiCrawler!
            W: Forward                  1: Sit
            A: Turn left                2: Stand
            S: Backward                 3: Wave
            D: Turn right               4: Dance
            Q: Turn Angle Left          5: Swim
            X: Turn Angle Right         6: Pushup
            Z: Ready Position           7: Twist
            E: Look left                8: Handwork
            R: Look up                  F: Look down
            I: Tap Front Right
            O: Tap Front Left           P: Tap Rear Right
            ;: Tap Rear Left            [: Sway All Legs
            ]: Point Movement           =: Stand Tall
            -: Stretch Out              `: Wiggle (3 sec)
            G: Glance Left             
        '''

    def show_info(self):
        print("\033[H\033[J",end='')  # clear terminal windows
        print(self.manual)

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

    def twist(self, speed):
        new_step=[[50, 50, -80], [50, 50, -80],[50, 50, -80], [50, 50, -80]]
        for i in range(4):
            for inc in range(30,60,5):
                rise = [50,50,(-80+inc*0.5)]
                drop = [50,50,(-80-inc)]

                new_step[i]=rise
                new_step[(i+2)%4] = drop
                new_step[(i+1)%4] = rise
                new_step[(i-1)%4] = drop
                self.picrawler.do_step(new_step,speed)

    ##"[[right front], [left front], [right rear], [left rear]]")

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

    def sit_down(self):
        # Assuming these are the commands to lower the legs
        sit_down_steps = [[50, 90, 90], [50, 90, 90], [50, 90, 90], [50, 90, 90]]
        self.picrawler.do_step(sit_down_steps, speed=1)
        sit_down_steps = [[50, 60, 60], [50, 60, 60], [0, 60, 60], [0, 60, 60]]
        self.picrawler.do_step(sit_down_steps, speed=1)
        sit_down_steps = [[50, 30, 30], [50, 30, 30], [0, 30, 30], [0, 30, 30]]
        self.picrawler.do_step(sit_down_steps, speed=1)
        sit_down_steps = [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]]
        self.picrawler.do_step(sit_down_steps, speed=1)

    def excited(self, speed, stop_event):
        new_step = [[50, 50, -80], [50, 50, -80], [50, 50, -80], [50, 50, -80]]
        while not stop_event.is_set():
            for i in range(4):
                for inc in range(30, 60, 80):
                    if stop_event.is_set():
                        break
                    rise = [50, 50, (-80 + inc * 0.5)]
                    drop = [50, 50, (-80 - inc)]
                    new_step[i] = rise
                    new_step[(i + 2) % 4] = drop
                    new_step[(i + 1) % 4] = rise
                    new_step[(i - 1) % 4] = drop
                    self.picrawler.do_step(new_step, speed)

    async def move_along_now(self):
        self.show_info()
        while True:
            key = readchar.readkey().lower()
            if key in ('wsadqexzercf12345678iop;[]=-`gk'):
                if key == 'w':
                    self.picrawler.do_action('forward', 1, self.speed)
                elif key == 's':
                    self.picrawler.do_action('backward', 1, self.speed)
                elif key == 'a':
                    self.picrawler.do_action('turn left', 1, self.speed)
                elif key == 'd':
                    self.picrawler.do_action('turn right', 1, self.speed)
                elif key == 'q':
                    self.picrawler.do_action('turn left angle', 1, self.speed)
                elif key == 'x':
                    self.picrawler.do_action('turn right angle', 1, self.speed)
                elif key == 'z':
                    self.picrawler.do_action('ready', 1, self.speed)
                elif key == 'e':
                    self.picrawler.do_action('look left', 1, self.speed)
                elif key == 'c':
                    self.picrawler.do_action('look right', 1, self.speed)
                elif key == 'r':
                    self.picrawler.do_action('look up', 1, self.speed)
                elif key == 'f':
                    self.picrawler.do_action('look down', 1, self.speed)
                elif key == '1':
                    self.picrawler.do_action('sit', 1, self.speed)
                elif key == '2':
                    self.picrawler.do_action('stand', 1, self.speed)
                elif key == '3':
                    self.picrawler.do_action('wave', 1, self.speed)
                elif key == '4':
                    self.picrawler.do_action('dance', 1, self.speed)
                elif key == '5':
                    self.swimming(self.speed)
                elif key == '6':
                    self.pushup(self.speed)
                elif key == '7':
                    self.twist(self.speed)
                elif key == '8':
                    self.handwork(self.speed)
                # New movements from new_movements.py:
                elif key == 'i':
                    self.new_movements.tap_front_right()
                elif key == 'o':
                    self.new_movements.tap_front_left()
                elif key == 'p':
                    self.new_movements.tap_rear_right()
                elif key == ';':
                    self.new_movements.tap_rear_left()
                elif key == '[':
                    self.new_movements.sway_all_legs()
                elif key == ']':
                    # Iterate over each step/frame returned by point()
                    for step in self.new_movements.point():
                        self.picrawler.do_step(step, self.speed)
                        sleep(0.1)
                elif key == '=':
                    self.new_movements.stand_tall()
                elif key == '-':
                    self.new_movements.stretch_out()
                elif key == '`':
                    # Run wiggle for 3 seconds then cancel
                    wiggle_task = asyncio.create_task(self.new_movements.wiggle())
                    await asyncio.sleep(3)
                    wiggle_task.cancel()
                    try:
                        await wiggle_task
                    except:
                        pass
                elif key == 'g':
                    await self.new_movements.glance(direction="left", angle=30, speed=self.speed)
                sleep(0.05)
                self.show_info()
            elif key == readchar.key.CTRL_C:
                print("\n Quit")
                break
            sleep(0.02)


if __name__ == "__main__":
    robot_keyboard = RobotKeyboard()
    asyncio.run(robot_keyboard.move_along_now())
