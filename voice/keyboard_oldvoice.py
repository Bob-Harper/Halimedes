from time import sleep
import readchar
import asyncio
import threading
from classes.new_movements import NewMovements  # New movements not in Picrawler
from classes.picrawler import Picrawler  # Robot movement library
from robot_hat import TTS
 

class RobotKeyboard:
    def __init__(self, host='192.168.0.101', port=5000):
        self.speed = 99
        self.debug_messages = []  # Store debug messages
        self.picrawler = Picrawler()
        self.word1 = "This is so exciting!    What are we going to do tonight, Bob?"
        self.word2 = "The same thing we do every night, Hal.  We try to take over the world!"
        self.tts1 = TTS(engine='espeak')
        self.tts1.espeak_params(amp=50, speed=220, gap=2, pitch=98)  # amp = volume, speed = 80 to 260, gap = time between words, pitch 0-98 deep or high voice
        self.tts2 = TTS(engine='espeak')
        self.tts2.espeak_params(amp=50, speed=200, gap=2, pitch=2)
        # self.llm = LLMCommunicator(host, port)
        self.new_moves = NewMovements(self.picrawler)  # Pass picrawler instance to NewMovements
        # self.mic_index = 1
        self.manual = '''
        Press keys on keyboard to control Halimedes

        W: Forward            1: Sit        Y: Tap Front Right
        A: Turn left          2: Stand      U: Tap Front Left
        S: Backward           3: Wave       I: Tap Rear Right
        D: Turn right         4: Dance      O: Tap Rear Left
        Q: Small Left         5: Swim       P: Tap All
        E: Small Right        6: Pushup     G: Stand Tall
        X: Ready Position     7: Twist      H: Point (WIP)
                              8: Handwork   J: Sway
        Z: Look Left                        K: Rest
        C: Look Right
        R: Look up            9: Pinky and the Brain
        F: Look down          0: Listen and Respond (WIP)

        Press Space Bar to Quit
        '''

    def add_debug_message(self, message):
        """Add a message to the debug queue."""
        if len(self.debug_messages) > 10:  # Limit to the last 10 messages
            self.debug_messages.pop(0)
        self.debug_messages.append(message)

    def show_info(self):
        """Show debug messages above the keymapping instructions."""
        print("\033[H\033[J", end='')  # Clear terminal window
        print("\n--- Debug Messages ---")
        for msg in self.debug_messages:
            print(msg)
        print("\n--- Key Controls ---")
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

    def speak_and_dance(self, tts1, word1, word2, speed):
        stop_event = threading.Event()

        # Create a thread for speaking
        speak_thread = threading.Thread(target=self.tts1.say, args=(word1,))
        speak_thread2 = threading.Thread(target=self.tts2.say, args=(word2,))
        # Create a thread for dancing
        dance_thread = threading.Thread(target=self.excited, args=(speed, stop_event))
        sit_thread = threading.Thread(target=self.sit_down)
        # Start both threads
        speak_thread.start()
        dance_thread.start()

        # Wait for the speaking thread to finish
        speak_thread.join()
            # Signal the dancing thread to stop
        stop_event.set()
            # Wait for the dancing thread to finish
        dance_thread.join()

        sit_thread.start()
        speak_thread2.start()
        speak_thread2.join()
        sit_thread.join()

    async def move_along_now(self):
        self.show_info()
        while True:
            key = readchar.readkey()
            key = key.lower()
            if key in ('wsadqexzcrf1234567890yuiopgjkl'):
                if 'w' == key:
                    self.picrawler.do_action('forward', 1, self.speed)
                elif 's' == key:
                    self.picrawler.do_action('backward', 1, self.speed)
                elif 'a' == key:
                    self.picrawler.do_action('turn left', 1, self.speed)
                elif 'd' == key:
                    self.picrawler.do_action('turn right', 1, self.speed)
                elif 'q' == key:
                    self.picrawler.do_action('small left', 1, self.speed)
                elif 'e' == key:
                    self.new_moves.small_right()
                elif 'x' == key:
                    self.picrawler.do_action('ready', 1, self.speed)
                elif 'z' == key:
                    self.picrawler.do_action('look left', 1, self.speed)
                elif 'c' == key:
                    self.picrawler.do_action('look right', 1, self.speed)
                elif 'r' == key:
                    self.picrawler.do_action('look up', 1, self.speed)
                elif 'f' == key:
                    self.picrawler.do_action('look down', 1, self.speed)
                elif 'y' == key:
                    self.new_moves.tap_front_right()
                elif 'u' == key:
                    self.new_moves.tap_front_left()
                elif 'i' == key:
                    self.new_moves.tap_rear_right()
                elif 'o' == key:
                    self.new_moves.tap_rear_left()
                elif 'p' == key:
                    self.new_moves.tap_all_legs()
                elif 'g' == key:
                    self.new_moves.stand_tall()
                # elif 'h' == key:
                    # self.new_moves.point()
                elif 'j' == key:
                    self.new_moves.sway_all_legs()
                elif 'k' == key:
                    self.new_moves.sit_down()
                elif '1' == key:
                    self.picrawler.do_action('sit', 1, self.speed)
                elif '2' == key:
                    self.picrawler.do_action('stand', 1, self.speed)
                elif '3' == key:
                    self.picrawler.do_action('wave', 1, self.speed)
                elif '4' == key:
                    self.picrawler.do_action('dance', 1, self.speed)
                elif '5' == key:
                    self.swimming(self.speed)
                elif '6' == key:
                    self.pushup(self.speed)
                elif '7' == key:
                    self.twist(self.speed)
                elif '8' == key:
                    self.handwork(self.speed)
                elif '9' == key:
                    self.speak_and_dance(self.tts1, self.word1, self.word2, self.speed)
                # elif '0' == key:
                #     asyncio.create_task(self.test_capture_and_transcribe(self.tts1, self.mic_index, self.speed))
                await asyncio.sleep(0.05)
                self.show_info()
            elif key == readchar.key.SPACE:
                print("\n Quitting")
                await asyncio.sleep(2)
                print("\033[H\033[J",end='')  # clear terminal windows
                break

            await asyncio.sleep(0.2)


if __name__ == "__main__":
    robot_keyboard = RobotKeyboard()
    asyncio.run(robot_keyboard.move_along_now())
