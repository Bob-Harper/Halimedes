import random
# import stuff
# EmotionManager NOT USED YET.  EXAMPLE PLACEHOLDER
# EmotionHandler used for CATEGORIZING tags and sound/action/expressions to valid choices
# emotional_sounds_manager.py for examples and ideas on how to implement.
import time
from nltk.sentiment import SentimentIntensityAnalyzer
from nrclex import NRCLex

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


class EmotionCategorizer:
    def __init__(self):
        self.sia = SentimentIntensityAnalyzer()
        self.emotion_categories = ['fear', 'anger', 'anticipation', 'trust', 'surprise',
                                    'positive', 'negative', 'sadness', 'disgust', 'joy']

    def analyze_text_emotion(self, text):
        if not text:
            return "neutral"

        # Use NRCLex for emotion detection
        nrc_analysis = NRCLex(text)
        nrc_emotions = nrc_analysis.raw_emotion_scores # type: ignore

        # Normalize to include all emotion categories with a score of 0 if missing
        nrc_emotions = {emotion: nrc_emotions.get(emotion, 0) for emotion in self.emotion_categories}

        # Combine with SIA polarity for additional insight
        sia_scores = self.sia.polarity_scores(text)
        if sia_scores['compound'] >= 0.05:
            nrc_emotions['positive'] += sia_scores['compound']
        elif sia_scores['compound'] <= -0.05:
            nrc_emotions['negative'] += abs(sia_scores['compound'])

        # Identify the predominant emotion
        # nrc_emotions: Dict[str, float]
        predominant_emotion = max(
            nrc_emotions.items(),
            key=lambda kv: kv[1]
        )[0]
        # Return the emotion if significant, otherwise "neutral"
        return predominant_emotion if nrc_emotions[predominant_emotion] > 0 else "neutral"

