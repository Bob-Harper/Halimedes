from .robot_hat import Ultrasonic, Pin
from .picrawler import Picrawler
from .picrawler_extended import PicrawlerExtended
from helpers.response_manager import Response_Manager
import asyncio
import collections


class ExplorerRobot:
    def __init__(self, alert_distance=15, speed=80, grid_width=8, grid_height=8):
        # Initialize the ultrasonic sensor
        self.sonar = Ultrasonic(Pin("D2"), Pin("D3"))
        self.crawler = Picrawler()
        self.new_movements = PicrawlerExtended(self.crawler)
        self.alert_distance = alert_distance  # Distance to stop or avoid (in cm)
        self.speed = speed  # Movement speed
        self.running = True
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.grid = [[" " for _ in range(grid_width)] for _ in range(grid_height)]
        self.current_position = (0, 0)
        self.grid[self.current_position[1]][self.current_position[0]] = "X"
        self.direction = (0, -1)  # Default direction is "up" (forward)
        self.response = Response_Manager(self.crawler)


    def read_distance(self):
        """Read distance from ultrasonic sensor."""
        distance = self.sonar.read()
        if distance == -1:
            print("Ultrasonic sensor timeout or error.")
        return distance

    async def backtrack_to_unexplored(self):
        """Backtrack to the nearest unexplored cell using BFS."""
        queue = collections.deque([(self.current_position, [])])
        visited = set()

        while queue:
            (cx, cy), path = queue.popleft()
            if (cx, cy) in visited:
                continue
            visited.add((cx, cy))

            if self.grid[cy][cx] == " ":
                print(f"Backtracking to unexplored cell at ({cx}, {cy}).")
                for step in path:
                    direction, (dx, dy) = step
                    self.crawler.do_action(f"turn {direction}", 1, self.speed)
                    self.crawler.do_action("forward", 1, self.speed)
                    self.current_position = (cx + dx, cy + dy)
                return

            directions = {
                "forward": (0, -1),
                "backward": (0, 1),
                "left": (-1, 0),
                "right": (1, 0),
            }
            for direction, (dx, dy) in directions.items():
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < self.grid_width and 0 <= ny < self.grid_height:
                    if (nx, ny) not in visited:
                        queue.append(((nx, ny), path + [(direction, (dx, dy))]))

        print("No unexplored cells remaining.")
        await self.response.self.response.speak_with_flite("All areas have been mapped. Stopping exploration.")
        self.running = False

    def update_direction(self, turn):
        """Update the current direction based on the turn."""
        directions = {
            (0, -1): {"left": (-1, 0), "right": (1, 0)},  # Moving up
            (0, 1): {"left": (1, 0), "right": (-1, 0)},   # Moving down
            (-1, 0): {"left": (0, 1), "right": (0, -1)},  # Moving left
            (1, 0): {"left": (0, -1), "right": (0, 1)},   # Moving right
        }
        self.direction = directions[self.direction][turn]

    async def explore_and_map(self):
        """Explore the environment and map it."""
        try:
            while self.running:
                # Read the current distance
                distance = self.read_distance()
                print(f"Distance: {distance} cm")
                
                # Update the current position on the grid
                if 0 <= self.current_position[0] < self.grid_width and 0 <= self.current_position[1] < self.grid_height:
                    self.grid[self.current_position[1]][self.current_position[0]] = "X"
                else:
                    print(f"Error: Position out of bounds: {self.current_position}")
                    self.running = False
                    break
                
                # Decide what to do next
                if distance > self.alert_distance or distance == -1:
                    print("Path is clear. Moving forward.")
                    # Calculate the next position based on direction
                    next_position = (
                        self.current_position[0] + self.direction[0],
                        self.current_position[1] + self.direction[1],
                    )
                    # Check if the next position is within bounds
                    if 0 <= next_position[0] < self.grid_width and 0 <= next_position[1] < self.grid_height:
                        self.crawler.do_action("forward", 1, self.speed)
                        self.current_position = next_position
                    else:
                        print(f"Next position out of bounds: {next_position}. Turning instead.")
                        await self.response.self.response.speak_with_flite("Boundary detected. Recalculating.")
                        self.crawler.do_action("turn left", 1, self.speed)
                        self.update_direction("left")
                else:
                    print("Obstacle detected!")
                    await self.response.self.response.speak_with_flite("Obstacle detected! Recalculating.")
                    self.crawler.do_action("backward", 1, self.speed)
                    await asyncio.sleep(1)
                    
                    # Turn left and update direction
                    self.crawler.do_action("turn left", 1, self.speed)
                    self.update_direction("left")

                # Print the updated map
                for row in self.grid:
                    print("".join(row))

                await asyncio.sleep(0.2)  # Add a short delay to avoid rapid looping

        except KeyboardInterrupt:
            print("Exploration stopped manually.")
        finally:
            self.shutdown()
        """Explore the environment and map it."""
        try:
            while self.running:
                # Read the current distance
                distance = self.read_distance()
                print(f"Distance: {distance} cm")
                
                # Update the current position on the grid
                if 0 <= self.current_position[0] < self.grid_width and 0 <= self.current_position[1] < self.grid_height:
                    self.grid[self.current_position[1]][self.current_position[0]] = "X"
                else:
                    print(f"Error: Position out of bounds: {self.current_position}")
                    self.running = False
                    break
                
                # Decide what to do next
                if distance > self.alert_distance or distance == -1:
                    print("Path is clear. Moving forward.")
                    self.crawler.do_action("forward", 1, self.speed)
                    self.current_position = (
                        self.current_position[0] + self.direction[0],
                        self.current_position[1] + self.direction[1],
                    )
                else:
                    print("Obstacle detected!")
                    await self.response.self.response.speak_with_flite("Obstacle detected! Recalculating.")
                    self.crawler.do_action("backward", 1, self.speed)
                    await asyncio.sleep(1)
                    
                    # Turn left and update direction
                    self.crawler.do_action("turn left", 1, self.speed)
                    self.update_direction("left")

                # Print the updated map
                for row in self.grid:
                    print("".join(row))

                await asyncio.sleep(0.2)  # Add a short delay to avoid rapid looping

        except KeyboardInterrupt:
            print("Exploration stopped manually.")
        finally:
            self.shutdown()

    def print_grid(self):
        """Print the current exploration grid."""
        for row in self.grid:
            print(" ".join(row))
        print("\n")

    def shutdown(self):
        """Gracefully stop the robot."""
        self.running = False
        self.crawler.do_action("stop")
        print("Robot stopped gracefully.")


if __name__ == "__main__":
    robot = ExplorerRobot(alert_distance=15, speed=80, grid_width=8, grid_height=8)
    asyncio.run(robot.explore_and_map())
