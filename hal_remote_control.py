import time
import asyncio
from classes.ios_controller import SunFounderController
from helpers.picrawler import Picrawler
from helpers.new_movements import NewMovements

class RobotRemoteControl:
    def __init__(self):
        self.controller = SunFounderController()
        self.picrawler = Picrawler()
        self.new_movements = NewMovements(self.picrawler)
        self.speed = 85  # Default speed

    def update_speed(self, value):
        """ Update speed value from slider """
        try:
            speed_value = int(value)
            if 1 <= speed_value <= 99:
                self.speed = speed_value
                print(f"Updated speed: {self.speed}")
        except ValueError:
            print("Invalid speed value received.")

    def update_turn_angle(self, value):
        """ Update turn_angle value from slider """
        try:
            turn_angle = int(value)
            if 10 <= turn_angle <= 45:
                self.turn_angle = turn_angle
                print(f"Updated turn_angle: {self.turn_angle}")
        except ValueError:
            print("Invalid turn_angle value received.")

    def process_input(self, data):
        """ Handle incoming commands from iOS controller """
        print(f"Received: {data}")

        if data.get("A") is not None:  # Update speed slider
            self.update_speed(data["A"])
        if data.get("B") is not None:  # Update turn_angle slider
            self.update_turn_angle(data["B"])

        if data.get("I"):  # Forward
            self.picrawler.do_action("forward", 1, self.speed)
        elif data.get("S"):  # Backward
            self.picrawler.do_action("backward", 1, self.speed)
        elif data.get('M'):  # Turn Left
            turn_angle = data.get('B', 30)  # Get slider B value, default to 30
            self.picrawler.do_action('turn left angle', 1, self.speed, angle=turn_angle)
        elif data.get('R'):  # Turn Right
            turn_angle = data.get('B', 30)  # Get slider B value, default to 30
            self.picrawler.do_action('turn right angle', 1, self.speed, angle=turn_angle)
        elif data.get("Q"):  # Sit
            self.picrawler.do_action("sit", 1, self.speed)

    async def run(self):
        """ Main loop to listen for remote inputs """
        self.controller.start()
        print("Remote control ready. Waiting for commands...")

        try:
            while True:
                if self.controller.is_received:
                    data = self.controller.getall()
                    self.process_input(data)
                await asyncio.sleep(0.1)

        except KeyboardInterrupt:
            print("\nRemote control stopped.")
            self.controller.close()

# Start remote control
if __name__ == "__main__":
    remote = RobotRemoteControl()
    asyncio.run(remote.run())
