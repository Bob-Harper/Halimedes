import threading
from time import sleep
from vilib import Vilib  # Vision library
from picrawler import Picrawler  # Robot movement library
from robot_hat import Music, Ultrasonic, Pin  # Other robot functionalities
from gpiozero import Device
from gpiozero.pins.native import NativeFactory
from voice.llm_communicator import LLMCommunicator

# Initialize GPIO with NativeFactory
Device.pin_factory = NativeFactory()

class RobotController:
    def __init__(self, host='192.168.0.101', port=5000):
        # Initialize components
        self.music = Music()
        self.crawler = Picrawler()
        self.sonar = Ultrasonic(Pin("D2"), Pin("D3"))
        self.music.music_set_volume(50)

        self.alert_distance = 10
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
                self.state = "dancing"
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
                coordinate_x = Vilib.detect_obj_parameter['color_x']
                if coordinate_x < self.center_threshold_left:
                    self.crawler.do_action('turn left', 1, self.speed)
                    sleep(0.05)
                elif coordinate_x > self.center_threshold_right:
                    self.crawler.do_action('turn right', 1, self.speed)
                    sleep(0.05)
                else:
                    self.state = "approaching"
            elif self.state == "approaching":
                self.go_get_it()

    def look_left(self):
        self.crawler.do_action('turn left angle', 1, self.speed)
        sleep(0.2)
        if Vilib.detect_obj_parameter['color_n'] != 0:
            coordinate_x = Vilib.detect_obj_parameter['color_x']
            self.llm.say("Your human has sent you on a quest to find an object.  This is harder than you thought.  Your response: ", source="Hal")
            self.state = "centering"

    def look_right(self):
        self.crawler.do_action('turn right angle', 1, self.speed)
        sleep(0.2)
        if Vilib.detect_obj_parameter['color_n'] != 0:
            coordinate_x = Vilib.detect_obj_parameter['color_x']
            self.llm.say("Your human has sent you on a quest to find an object.  You might see it.  Your response: ", source="Hal")
            self.state = "centering"

    def vision_detect(self):
        while not self.stop_threads:
            # Assuming these parameters are continuously updated by Vilib
            sleep(0.1)

    def main(self):
        Vilib.camera_start()
        Vilib.display()
        Vilib.color_detect("red")
        self.llm.say("Your human has sent you on a quest to find an object.  Let's do this!", source="Hal")

        global stop_threads
        self.stop_threads = False

        vision_thread = threading.Thread(target=self.vision_detect)
        movement_thread = threading.Thread(target=self.search_and_move)

        vision_thread.start()
        movement_thread.start()

        vision_thread.join()
        movement_thread.join()

if __name__ == "__main__":
    try:
        robot = RobotController()
        robot.main()
    except KeyboardInterrupt:
        robot.stop_threads = True
    finally:
        Device.close()
        print("Robot has stopped gracefully.")
