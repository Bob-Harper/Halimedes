from .picrawler import Picrawler
from time import sleep
import readchar
import asyncio
from .picrawler_extended import PicrawlerExtended


class RobotKeyboard:
    def __init__(self):
        self.speed = 99
        self.picrawler = Picrawler()
        self.new_movements = PicrawlerExtended(self.picrawler)
        self.manual = '''
        Press keys on keyboard to control PiCrawler!
            W: Forward                  1: Sit
            S: Backward                 2: Stand
            A: Turn Left                3: Wave
            D: Turn Right               4: Dance
            Q: Turn Angle Left          5: Swim (3x)
            X: Turn Angle Right         6: Pushup (3x)
            7: Twist
            E: Look Left                8: Handwork
            C: Look Right               R: Look Up
            F: Look Down                I: Tap Front Right
            O: Tap Front Left           P: Tap Rear Right
            ;: Tap Rear Left            
            =: Stand Tall               -: Stretch Out
            `: Wiggle (3 sec)           G: Glance Left then Forward
            H: Glance Right then Forward  J: Glance Left, Forward, Right, Forward
        '''

    def show_info(self):
        print("\033[H\033[J", end='')  # clear terminal
        print(self.manual)

    async def move_along_now(self):
        self.show_info()
        while True:
            key = readchar.readkey().lower()
            # Allowed keys based on the actual mapping
            if key in ('w', 's', 'a', 'd', 'q', 'x', 'z', 'e', 'c', 'r', 'f',
                       '1', '2', '3', '4', '5', '6', '7', '8', 'i', 'o', 'p',
                       ';', '=', '-', '`', 'g', 'h', 'j'):
                if key == 'w':
                    self.picrawler.do_action('forward', 1, self.speed)
                elif key == 's':
                    self.picrawler.do_action('backward', 1, self.speed)
                elif key == 'a':
                    self.picrawler.do_action('turn left', 1, self.speed)
                elif key == 'd':
                    self.picrawler.do_action('turn right', 1, self.speed)
                elif key == 'q':
                    self.picrawler.do_action('turn left angle', 1, self.speed, angle=15)
                elif key == 'x':
                    self.picrawler.do_action('turn right angle', 1, self.speed, angle=15)
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
                    self.new_movements.swimming(count=3, speed=self.speed)
                elif key == '6':
                    self.new_movements.pushup(3, speed=self.speed)
                elif key == '7':
                    self.new_movements.twist(speed=self.speed)
                elif key == '8':
                    self.new_movements.handwork(speed=self.speed)
                elif key == 'i':
                    self.new_movements.tap_front_right()
                elif key == 'o':
                    self.new_movements.tap_front_left()
                elif key == 'p':
                    self.new_movements.tap_rear_right()
                elif key == ';':
                    self.new_movements.tap_rear_left()
                elif key == '=':
                    self.new_movements.stand_tall()
                elif key == '-':
                    self.new_movements.stretch_out()
                elif key == '`':
                    wiggle_task = asyncio.create_task(self.new_movements.wiggle())
                    await asyncio.sleep(3)
                    wiggle_task.cancel()
                    try:
                        await wiggle_task
                    except:
                        pass
                elif key == 'g':
                    await self.new_movements.glance(direction="left", angle=25, speed=self.speed)
                    sleep(0.5)
                    await self.new_movements.glance(direction="forward", angle=25, speed=self.speed)
                elif key == 'h':
                    await self.new_movements.glance(direction="right", angle=25, speed=self.speed)
                    sleep(0.5)
                    await self.new_movements.glance(direction="forward", angle=25, speed=self.speed)
                elif key == 'j':
                    await self.new_movements.glance(direction="left", angle=25, speed=self.speed)
                    sleep(0.5)
                    await self.new_movements.glance(direction="forward", angle=25, speed=self.speed)
                    sleep(0.5)
                    await self.new_movements.glance(direction="right", angle=25, speed=self.speed)
                    sleep(0.5)
                    await self.new_movements.glance(direction="forward", angle=25, speed=self.speed)
                sleep(0.05)
                self.show_info()
            elif key == readchar.key.CTRL_C:
                print("\n Quit")
                break
            sleep(0.02)


if __name__ == "__main__":
    robot_keyboard = RobotKeyboard()
    asyncio.run(robot_keyboard.move_along_now())
