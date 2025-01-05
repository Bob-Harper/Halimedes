from time import sleep
from vilib import Vilib  # Vision library
from picrawler import Picrawler  # Robot movement library
from robot_hat import Music, Ultrasonic, Pin  # Other robot functionalities
from gpiozero import Device
from gpiozero.pins.native import NativeFactory
from voice.llm_communicator import LLMCommunicator
import threading

# Initialize GPIO with NativeFactory
Device.pin_factory = NativeFactory()

class RobotController:
    def __init__(self, host='192.168.0.101', port=5000):
        # Initialize components
        self.music = Music()
        self.crawler = Picrawler()
        self.sonar = Ultrasonic(Pin("D2"), Pin("D3"))
        self.music.music_set_volume(50)

        self.alert_distance = 5
        self.speed = 80
        self.center_threshold_left = 140
        self.center_threshold_right = 180

        self.stop_threads = False
        self.state = "searching"

        self.llm = LLMCommunicator(host, port)

    def go_get_it(self):
        while not self.stop_threads:
            distance = self.sonar.read()
            print(distance)
            if distance < 0:
                pass
            elif distance > self.alert_distance:
                self.crawler.do_action('forward', 1, self.speed)
                sleep(0.2)
            elif distance <= self.alert_distance:
                self.found_it()
                self.state = "dancing"  # Assuming "dancing" state is for celebratory actions
                self.stop_threads = True
                break

    def found_it(self):
        self.crawler.do_action('push up', 1, self.speed)
        sleep(1)
        self.crawler.do_action('wave', 1, self.speed)
        self.llm.say("Your human has sent you on a quest to find an object.  YOU FOUND IT!  Your response: ", source="Hal")
        self.crawler.do_action('wave', 1, self.speed)
        sleep(0.5)

    def search_and_move(self):
        while not self.stop_threads:
            if self.state == "searching":
                self.crawler.do_action('turn left', 1, self.speed)
                sleep(0.05)
                self.look_left()
                self.look_right()

            elif self.state == "centering":
                if self.detect_red():
                    self.state = "approaching"
                    continue  # Skip unnecessary movement if already centered on red

                coordinate_x = Vilib.detect_obj_parameter.get('color_x', None)
                if coordinate_x is not None:
                    if coordinate_x < self.center_threshold_left:
                        self.music.sound_play_threading('./sounds/sign.wav', volume=100)
                        self.crawler.do_action('turn left', 1, self.speed)
                        sleep(0.05)
                    elif coordinate_x > self.center_threshold_right:
                        self.music.sound_play_threading('./sounds/sign.wav', volume=100)
                        self.crawler.do_action('turn right', 1, self.speed)
                        sleep(0.05)
                    else:
                        self.state = "approaching"
                else:
                    self.state = "searching"

            elif self.state == "approaching":
                self.approach_object()

    def look_left(self):
        self.crawler.do_action('turn left angle', 1, self.speed)
        sleep(0.2)
        if self.detect_red():
            self.state = "centering"

    def look_right(self):
        self.crawler.do_action('turn right angle', 1, self.speed)
        sleep(0.2)
        if self.detect_red():
            self.state = "centering"

    def approach_object(self):
        while not self.stop_threads:
            distance = self.sonar.read()
            if distance < 0:
                pass
            elif distance > self.alert_distance:
                self.crawler.do_action('forward', 1, self.speed)
                sleep(0.2)
            elif distance <= self.alert_distance:
                self.found_it()
                break

    def detect_red(self):
        # Example: Check if red is detected (replace with actual detection logic)
        # Assuming Vilib.detect_obj_parameter is updated by vision system
        if 'color' in Vilib.detect_obj_parameter:
            return Vilib.detect_obj_parameter['color'] == "red"
        return False

    def vision_detect(self):
        while not self.stop_threads:
            # Check for color detection (modify as per actual implementation)
            if self.detect_red():
                self.state = "centering"

            # Assuming these parameters are continuously updated by Vilib
            sleep(0.1)

    def main(self):
        Vilib.camera_start()
        Vilib.display()
        self.llm.say("Your human has sent you on a quest to find an object. find a funny way to say:  Let's do this!", source="Hal")

        self.stop_threads = False

        vision_thread = threading.Thread(target=self.vision_detect)
        movement_thread = threading.Thread(target=self.search_and_move)

        vision_thread.start()
        movement_thread.start()

        try:
            vision_thread.join()
            movement_thread.join()
        except KeyboardInterrupt:
            self.stop_threads = True
            vision_thread.join()
            movement_thread.join()
        finally:
            self.sonar.close()
            print("Robot has stopped gracefully.")

if __name__ == "__main__":
    try:
        robot = RobotController()
        robot.main()
    except KeyboardInterrupt:
        robot.stop_threads = True
    finally:
        # Close any necessary resources here
        pass
