import random
import time


class EmotionManager:
    def __init__(self):
        self.current_emotion = 'neutral'
        self.last_update = time.time()

    def update_emotion(self):
        if time.time() - self.last_update > 300:  # every 5 minutes
            self.current_emotion = random.choice(['happy', 'neutral', 'cautious', 'curious', 'sleepy'])
            self.last_update = time.time()

    def get_emotion(self):
        return self.current_emotion
