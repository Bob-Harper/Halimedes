from helpers.picrawler import Picrawler
from time import sleep
import readchar
import asyncio
from helpers.new_movements import NewMovements


class RobotKeyboard:
    def __init__(self):
        self.speed = 85
        self.picrawler = Picrawler()
        self.new_movements = NewMovements(self.picrawler)
        self.manual = '''
        Press keys to test PiCrawler's leg-specific wave:
            Q: Wave with Front Left leg (lf)         
            W: Wave with Front Right leg (rf)      
            A: Wave with Rear Left leg (lr)        
            S: Wave with Rear Right leg (rr)        
        CTRL+C to quit.
        '''

    def show_info(self):
        print("\033[H\033[J", end='')  # clear terminal window
        print(self.manual)

    async def move_along_now(self):
        self.show_info()
        leg_mapping = {'q': 'lf', 'w': 'rf', 'a': 'lr', 's': 'rr'}
        while True:
            key = readchar.readkey().lower()
            if key in leg_mapping:
                leg = leg_mapping[key]
                print(f"\n[DEBUG] Triggering wave on leg: {leg}")
                self.new_movements.wave(speed=self.speed, leg=leg)  # Trigger wave for selected leg
            elif key == readchar.key.CTRL_C:
                print("\nQuitting.")
                break
            sleep(0.02)  # Minor delay for smoother control


if __name__ == "__main__":
    robot_keyboard = RobotKeyboard()
    asyncio.run(robot_keyboard.move_along_now())
