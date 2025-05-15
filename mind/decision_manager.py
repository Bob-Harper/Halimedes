# import stuff
# NOT USED YET.  EXAMPLE PLACEHOLDER
# emotional_sounds_manager.py for examples and ideas on how to implement.
import random


class DecisionManager:  # NOT USED YET.  EXAMPLE PLACEHOLDER
    def __init__(self, emotion_engine):
        self.emotion_engine = emotion_engine

    def should_act(self, stimulus_type):
        emotion = self.emotion_engine.get_emotion()
        
        # Basic personality: sleepy Hal doesn't like to move unless stimulated
        if emotion == 'sleepy' and stimulus_type == 'movement':
            return random.random() < 0.3  # 30% chance he'll act
        elif emotion == 'happy' and stimulus_type == 'greeting':
            return True  # Always greet if happy
        elif emotion == 'cautious' and stimulus_type == 'unknown_person':
            return random.random() < 0.5  # 50% chance
        else:
            return True  # Default allow
