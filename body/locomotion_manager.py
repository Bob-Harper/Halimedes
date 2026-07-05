# body/locomotion_manager.py

class LocomotionManager:
    def __init__(self, picrawler):
        self.picrawler = picrawler

    def stop(self):
        # Picrawler stop is synchronous, but wrap for consistency
        self.picrawler.stop()

    def step_back(self):
        self.picrawler.backward(1)

    def back_up(self):
        self.picrawler.backward(2)

    def turn_away_left(self):
        self.picrawler.turn_left(1)

    def turn_away_right(self):
        self.picrawler.turn_right(1)

    def turn_angle_left(self, angle=15):
        self.picrawler.turn_left_angle(1, angle=angle)

    def turn_angle_right(self, angle=15):
        self.picrawler.turn_right_angle(1, angle=angle)

    def recover_posture(self):
        self.picrawler.stand(1)

    def brace(self):
        # temporary until we define a real brace pose
        self.picrawler.stand_tall()

    def investigate_forward(self):
        self.picrawler.forward(1)

    def investigate_backward(self):
        self.picrawler.backward(1)

    def look_left(self):
        self.picrawler.look_left(1)

    def look_right(self):
        self.picrawler.look_right(1)

    def look_down(self):
        self.picrawler.look_down(1)

    def look_up(self):
        self.picrawler.look_up(1)

    def glance_left(self):
        self.picrawler.glance(direction="left", angle=25)

    def glance_right(self):
        self.picrawler.glance(direction="right", angle=25)

    def glance_forward(self):
        self.picrawler.glance(direction="forward", angle=25)
