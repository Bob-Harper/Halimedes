from nltk.sentiment import SentimentIntensityAnalyzer
from nrclex import NRCLex
import os
import random
import subprocess
from helpers.global_config import SOUND_ASSETS_PATH

""" 
multipliers adjust cadence to simulate emotional changes during speech compared to neutral default.
    Baseline values for Hal's signature voice
    baseline_pitch = 50
    baseline_speed = 0.88
 """

emotion_voice_map = {
    "joy": {"pitch_factor": 1.4, "speed_factor": 0.7},       # Higher pitch, faster speech
    "positive": {"pitch_factor": 1.3, "speed_factor": 0.8},  # Energetic and faster
    "neutral": {"pitch_factor": 1.0, "speed_factor": 1.0},   # Baseline voice
    "trust": {"pitch_factor": 1.15, "speed_factor": 0.9},    # Warm, steady, and slightly faster
    "surprise": {"pitch_factor": 1.5, "speed_factor": 0.6},  # Very excited and fast
    "fear": {"pitch_factor": 0.6, "speed_factor": 1.1},      # Low pitch, slower—hesitant
    "anger": {"pitch_factor": 0.5, "speed_factor": 1.15},     # Deep, intense, and slower
    "sadness": {"pitch_factor": 0.4, "speed_factor": 1.25},   # Very slow and low pitch
    "disgust": {"pitch_factor": 0.6, "speed_factor": 1.2},   # Low pitch, slower pace
    "anticipation": {"pitch_factor": 1.25, "speed_factor": 0.75}, # Faster and eager
    "negative": {"pitch_factor": 0.5, "speed_factor": 1.15},  # Deep pitch, slower
    "announcment": {"pitch_factor": 0.85, "speed_factor": 1.1},  # Neutral, slower
}


def get_voice_modifiers(emotion):
    """
    Retrieve the pitch and speed modifiers based on the emotion.
    If the emotion is not found, return the baseline (1.0 factors).
    """
    return emotion_voice_map.get(emotion, {"pitch_factor": 1.0, "speed_factor": 1.0})


class EmotionalSoundsManager:
    def __init__(self):
        self.emotion_base_dir = SOUND_ASSETS_PATH

    def get_emotion_directory(self, emotion):
        """Returns the appropriate sound directory for the given emotion."""
        emotion_dir = os.path.join(self.emotion_base_dir, emotion)
        if os.path.exists(emotion_dir):
            return emotion_dir
        else:
            print(f"Warning: No directory found for emotion '{emotion}'")
            return None

    def play_sound(self, emotion):
        """Play a sound from the corresponding emotion directory."""
        emotion_dir = self.get_emotion_directory(emotion)
        if not emotion_dir:
            return  # Directory doesn't exist, do nothing

        # Get all .wav files in the directory
        sound_files = [f for f in os.listdir(emotion_dir) if f.lower().endswith(".wav")]
        if not sound_files:
            print(f"No .wav files found in {emotion_dir}.")
            return

        # Choose a random sound and play it using aplay
        sound_file = os.path.join(emotion_dir, random.choice(sound_files))

        try:
            # print(f"Playing: {sound_file}")
            subprocess.run(["aplay", sound_file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

        except subprocess.CalledProcessError as e:
            print(f"Error playing sound: {e}")


class EmotionHandler:
    def __init__(self):
        self.sia = SentimentIntensityAnalyzer()
        self.emotion_categories = ['fear', 'anger', 'anticipation', 'trust', 'surprise',
                                    'positive', 'negative', 'sadness', 'disgust', 'joy']

    def analyze_text_emotion(self, text):
        if not text:
            return "neutral"

        # Use NRCLex for emotion detection
        nrc_analysis = NRCLex(text)
        nrc_emotions = nrc_analysis.raw_emotion_scores

        # Normalize to include all emotion categories with a score of 0 if missing
        nrc_emotions = {emotion: nrc_emotions.get(emotion, 0) for emotion in self.emotion_categories}

        # Combine with SIA polarity for additional insight
        sia_scores = self.sia.polarity_scores(text)
        if sia_scores['compound'] >= 0.05:
            nrc_emotions['positive'] += sia_scores['compound']
        elif sia_scores['compound'] <= -0.05:
            nrc_emotions['negative'] += abs(sia_scores['compound'])

        # Identify the predominant emotion
        predominant_emotion = max(nrc_emotions, key=nrc_emotions.get)

        # Return the emotion if significant, otherwise "neutral"
        return predominant_emotion if nrc_emotions[predominant_emotion] > 0 else "neutral"


