# tested optimized works well!
# 
from robot_hat import Ultrasonic, Pin
from helpers.picrawler import Picrawler
from helpers.new_movements import NewMovements
from helpers.response_utils import speak_with_flite
import time
import asyncio
import random


class ExplorerRobot:
    def __init__(self, alert_distance=15, speed=80):
        # Initialize the ultrasonic sensor
        self.sonar = Ultrasonic(Pin("D2"), Pin("D3"))
        self.crawler = Picrawler()
        self.new_movements = NewMovements(self.crawler)
        self.alert_distance = alert_distance  # Distance to stop or avoid (in cm)
        self.speed = speed  # Movement speed
        self.running = True

    def read_distance(self):
        """Read distance from ultrasonic sensor."""
        distance = self.sonar.read()
        if distance == -1:
            print("Ultrasonic sensor timeout or error.")
        return distance

    async def avoid_obstacles(self):
        """Obstacle avoidance logic with random initial direction."""
        try:
            while self.running:
                distance = self.read_distance()
                if distance != -1:
                    print(f"Distance: {distance} cm")

                if distance > self.alert_distance or distance == -1:
                    print("Path is clear. Moving forward.")
                    self.crawler.do_action("forward", 1, self.speed)
                else:
                    print("Obstacle detected. Stopping and analyzing options.")
                    await speak_with_flite("Obstacle detected. Stopping and analyzing options.")

                    # Step back
                    self.crawler.do_action("backward", 2, self.speed)
                    time.sleep(1)

                    # Randomly pick the first direction to check
                    initial_direction = random.choice(["left", "right"])
                    secondary_direction = "right" if initial_direction == "left" else "left"

                    # Check the initial direction
                    print(f"Turning {initial_direction} to check.")
                    self.crawler.do_action(f"turn {initial_direction}", 1, self.speed)
                    time.sleep(0.5)
                    initial_distance = self.read_distance()
                    await speak_with_flite(f"{initial_direction.capitalize()} distance is {initial_distance} centimeters.")

                    # Reset to forward direction
                    print("Resetting to forward direction.")
                    self.crawler.do_action(f"turn {secondary_direction}", 1, self.speed)
                    time.sleep(0.5)

                    # Check the secondary direction
                    print(f"Turning {secondary_direction} to check.")
                    self.crawler.do_action(f"turn {secondary_direction}", 1, self.speed)
                    time.sleep(0.5)
                    secondary_distance = self.read_distance()
                    await speak_with_flite(f"{secondary_direction.capitalize()} distance is {secondary_distance} centimeters.")

                    # Reset to forward direction
                    print("Resetting to forward direction.")
                    self.crawler.do_action(f"turn {initial_direction}", 1, self.speed)
                    time.sleep(0.5)

                    # Compare distances and decide where to go
                    if initial_distance == -1 and secondary_distance == -1:
                        direction = random.choice(["left", "right"])
                        print(f"Both sides are unclear. Turning {direction} by default.")
                        await speak_with_flite(f"Both sides are unclear. Turning {direction} because I can.")
                        self.crawler.do_action(f"turn {direction}", 1, self.speed)
                    elif initial_distance == secondary_distance:
                        direction = random.choice(["left", "right"])
                        print(f"Distances are equal. Turning {direction} because why not.")
                        await speak_with_flite(f"Distances are equal. Turning {direction} because why not.")
                        self.crawler.do_action(f"turn {direction}", 1, self.speed)
                    elif initial_distance >= secondary_distance:
                        print(f"Turning {initial_direction} seems safer.")
                        await speak_with_flite(f"Turning {initial_direction} seems safer. I think I'll go that way because I can.")
                        self.crawler.do_action(f"turn {initial_direction}", 1, self.speed)
                    else:
                        print(f"Turning {secondary_direction} seems safer.")
                        await speak_with_flite(f"Turning {secondary_direction} seems safer. I think I'll go that way because why not.")
                        self.crawler.do_action(f"turn {secondary_direction}", 1, self.speed)

                time.sleep(0.2)  # Short delay between sensor readings
        except KeyboardInterrupt:
            print("Exploration stopped manually.")
        finally:
            self.shutdown()

    def shutdown(self):
        """Gracefully stop the robot."""
        self.running = False
        self.crawler.do_action("stop")
        print("Robot stopped gracefully.")


if __name__ == "__main__":
    robot = ExplorerRobot(alert_distance=15, speed=99)
    asyncio.run(robot.avoid_obstacles())
