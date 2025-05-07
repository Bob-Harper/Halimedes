import asyncio
from time import sleep
import os
from body.ios_controller import SunFounderController
from body.picrawler import Picrawler
from body.picrawler_extended import PicrawlerExtended
from body.robot_hat import Pin, Ultrasonic, utils
from vision.vilib import Vilib
utils.reset_mcu()
sleep(0.5)

class RobotRemoteControl:
    def __init__(self):
        self.controller = SunFounderController()
        self.picrawler = Picrawler()
        self.new_movements = PicrawlerExtended(self.picrawler)
        self.speed = 85  # Default speed
        self.turn_angle = 30 # Default angle
        self.sonar = Ultrasonic(Pin("D2") ,Pin("D3"))

    @staticmethod
    def getIP():
        wlan0 = os.popen("ifconfig wlan0 |awk '/inet/'|awk 'NR==1 {print $2}'").readline().strip('\n')
        eth0 = os.popen("ifconfig eth0 |awk '/inet/'|awk 'NR==1 {print $2}'").readline().strip('\n')
        if wlan0 == '':
            wlan0 = None
        if eth0 == '':
            eth0 = None
        return wlan0,eth0

    def update_speed(self, value):
        """ Update speed value from slider """
        try:
            speed_value = int(value)
            if 1 <= speed_value <= 99:
                self.speed = speed_value
        except ValueError:
            print("Invalid speed value received.")

    def process_input(self, data):
        """ Handle incoming commands from iOS controller """
        # Slider values
        if data.get("A") is not None:  # Update speed slider
            self.update_speed(data["A"])
        if data.get("B"):  # Get turn_angle value
            self.turn_angle = data["B"]   

        # D-Pad controls, basic movements
        k_val = data.get('K')

        if k_val == 'forward':
            self.picrawler.do_action('forward',2,self.speed)     
        if k_val == 'backward':
            self.picrawler.do_action('backward',2,self.speed) 
        if k_val == 'left':
            self.picrawler.do_action('turn left angle',1,self.speed, angle=30) 
        if k_val == 'right':
            self.picrawler.do_action('turn right angle',1,self.speed, angle=30)      

        # Fine Control movements
        if data.get("I"):  # Forward
            self.picrawler.do_action("forward", 1, self.speed)
        if data.get("S"):  # Backward
            self.picrawler.do_action("backward", 1, self.speed)
        if data.get('M'):  # Turn Left
            turn_angle = data.get('B', 30)  # Get slider B value, default to 30
            self.picrawler.do_action('turn left angle', 1, self.speed, angle=turn_angle)
        if data.get('R'):  # Turn Right
            turn_angle = data.get('B', 30)  # Get slider B value, default to 30
            self.picrawler.do_action('turn right angle', 1, self.speed, angle=turn_angle)

        # High Speed movements
        if data.get("E"):  # Charge
            self.picrawler.do_action("forward", 4, 99)
        if data.get("F"):  # Retreat
            self.picrawler.do_action("backward", 4, 99)

        # Other Movements
        if data.get("T"):  # Sit
            self.picrawler.do_action("sit", 1, self.speed)
        if data.get("Q"):  # Stand
            self.picrawler.do_action("stand", 1, self.speed)
        if data.get("J"):  # Wave
            self.picrawler.do_action('wave', 1, self.speed)
        if data.get("N"):  # Look Left
            self.picrawler.do_action("look left", 1, self.speed)
        if data.get("O"):  # Look Right
            self.picrawler.do_action("look right", 1, self.speed)
        if data.get("C"):  # Look Up
            self.picrawler.do_action("look up", 1, self.speed)
        if data.get("P"):  # Sleep self.newmovements.sit_down
            self.new_movements.sit_down()
        if data.get("G"):  # Wiggle
            asyncio.run(self.new_movements.run_wiggle_for_seconds())
            
    async def run(self):
        self.controller.start()
        print("Remote control ready. Waiting for commands...")
        Vilib.camera_start(vflip=False,hflip=False)
        Vilib.display(local=False, web=True)
        
        wlan0, eth0 = RobotRemoteControl.getIP()
        ip = wlan0 if wlan0 else eth0

        try:
            while True:  # Only one loop
                if self.controller.is_received:
                    data = self.controller.getall()
                    self.process_input(data)

                # Send sensor & video feed data
                distance = self.sonar.read()
                self.controller.set("D", [0, distance])
                self.controller.set('video', f'http://{ip}:9000/mjpg')

                await asyncio.sleep(0.1)
        except KeyboardInterrupt:
            print("\nRemote control stopped.")
            self.controller.close()


# Start remote control
if __name__ == "__main__":
    remote = RobotRemoteControl()
    asyncio.run(remote.run())
