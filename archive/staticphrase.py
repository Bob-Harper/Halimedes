class HalimedesPhrases:
    def __init__(self, tts):
        self.tts = tts
        self.phrases = {
            1: "Whats up, boss?",
            2: "Hey, you cannot do that.",
            3: "Of course I can do that, watch me.",
            4: "I cannot do that? But I just did.",
            5: "Mooooooove bitch! get out the way!",
            6: "Goodnight human, I think it is cute that you always go to sleep expecting to wake up in the morning."
            }

    def speak_phrase(self, key):
        if key in self.phrases:
            phrase = self.phrases[key]
            self.tts.say(phrase)
        else:
            print(f"Phrase with key {key} not found.")
