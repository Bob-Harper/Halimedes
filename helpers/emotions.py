from nltk.sentiment import SentimentIntensityAnalyzer
from nrclex import NRCLex


class EmotionHandler:
    def __init__(self):
        """
        Initialize the EmotionHandler.
        Args:
            sound_base_dir (str): Path to the base directory containing emotion sound folders.
        """
        self.sia = SentimentIntensityAnalyzer()
        self.emotion_categories = ['fear', 'anger', 'anticipation', 'trust', 'surprise',
                                    'positive', 'negative', 'sadness', 'disgust', 'joy']

    def analyze_text_emotion(self, text):
        """
        Analyze the emotion of the given text using NRCLex and SIA.
        Args:
            text (str): Input text to analyze.

        Returns:
            str: The predominant emotion or "neutral".
        """
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
