import subprocess
import asyncio
from helpers.emotions import get_voice_modifiers
from helpers.emotions import EmotionHandler
from helpers.passive_sounds import PassiveSoundsManager
from helpers.new_movements import NewMovements
from nltk.tokenize import sent_tokenize, TreebankWordTokenizer
from nltk import pos_tag, RegexpParser


class Response_Manager:
    def __init__(self, picrawler_instance):
        self.crawler = picrawler_instance 

        # Hal's voicefile
        self.voice_path = "/home/msutt/hal/flitevox/cmu_us_rms.flitevox"
        # Baseline values to create Hal's signature voice
        self.baseline_pitch = 50
        self.baseline_speed = 0.88  # note below, value is counterintuitive
        """
        pitch: flite default 100 - higher/deeper voice correlates to higher/lower number
        speed: flite default 1.0 - higher values stretch (longer), lower compresses (shorter)
        """
        self.emotion_handler = EmotionHandler()
        self.sound_manager = PassiveSoundsManager()
        self.newmovements = NewMovements(self.crawler)

        # Expanded sound and action keywords for detection
        self.sound_keywords = ["whirr", "beep", "chirp", "giggle", "roar", "whoosh", "hum", "whistle"]
        self.action_keywords = ["wave", "rotate", "spark", "beam", "twist", "wiggle"]

    async def speak_with_flite(self, words, emotion="neutral"):
        """
        Speak using a single pitch and speed for the entire speech output.
        Baseline cadence for status, command response, and fallback processing.
        """
        # Get relative adjustment factors for pitch and speed
        emotion_settings = get_voice_modifiers(emotion)
        pitch_factor = emotion_settings["pitch_factor"]
        speed_factor = emotion_settings["speed_factor"]

        # Calculate modified pitch and speed
        pitch = int(self.baseline_pitch * pitch_factor)
        speed = round(self.baseline_speed * speed_factor, 2)

        try:
            command = [
                "flite",
                "-voice", self.voice_path,
                "--setf", f"int_f0_target_mean={pitch}",
                "--setf", f"duration_stretch={speed}",
                "-t", words,
            ]
            await asyncio.to_thread(subprocess.run, command, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")
        except FileNotFoundError:
            print("Flite command not found. Ensure it is installed and in the PATH.")

    async def speak_with_dynamic_flite(self, full_text):
        """
        Speak with adaptive pitch and speed modulation dynamically for each 
        sentence fragment.  Speech only, does not factor for sound effects or actions.
        """
        try:
            # Step 1: Use nltk to split text into meaningful fragments (sentences/clauses)
            fragments = sent_tokenize(full_text)

            # Step 2: Process each fragment individually
            for fragment in fragments:
                # Determine the emotion for the fragment
                fragment_emotion = self.emotion_handler.analyze_text_emotion(fragment)
                emotion_settings = get_voice_modifiers(fragment_emotion)
                pitch = int(self.baseline_pitch * emotion_settings["pitch_factor"])
                speed = round(self.baseline_speed * emotion_settings["speed_factor"], 2)
                # Speak the fragment with calculated pitch and speed
                command = [
                    "flite",
                    "-voice", self.voice_path,
                    "--setf", f"int_f0_target_mean={pitch}",
                    "--setf", f"duration_stretch={speed}",
                    "-t", fragment,
                ]
                await asyncio.to_thread(subprocess.run, command, check=True)

        except Exception as e:
            print(f"Error in adaptive speech, falling back to neutral: {e}")
            # Fallback to the default flite with no modulation
            await self.speak_with_flite(full_text)

    async def fully_dynamic_response(self, full_text):
        """
        Speak with adaptive pitch and speed modulation dynamically for each 
        sentence fragment. Processes text descriptions of sound effects and actions
        to swap them inline with actual sound effects and actions while conversing.
        """

        tokenizer = TreebankWordTokenizer()

        # Refined grammar to be stricter on what counts as sounds and actions
        chunk_grammar = r"""
            SOUND: {<JJ>*<NN|NNS>+<VBG>?<NN|NNS>*}  # Adjective + Nouns for valid sound descriptions
            ACTION: {<VB.*><DT|JJ|NN.*>+}           # Verb + Descriptive phrases for actions like "wobbles legs"
        """
        chunk_parser = RegexpParser(chunk_grammar)

        # Common irrelevant nouns to ignore (these can be customized)
        ignore_nouns = {"boy", "cat", "food", "fuel", "skills", "nevermind"}

        try:
            fragments = sent_tokenize(full_text)
            for fragment in fragments:
                print(f"[DEBUG] Analyzing fragment: '{fragment}'")

                tokens = tokenizer.tokenize(fragment)
                tagged_tokens = pos_tag(tokens)
                chunked_tree = chunk_parser.parse(tagged_tokens)

                buffer = []  
                sub_fragments = []

                for subtree in chunked_tree:
                    if isinstance(subtree, tuple):
                        buffer.append(subtree[0])

                    elif subtree.label() == "SOUND":
                        detected_sound = " ".join(word for word, _ in subtree)

                        # Skip irrelevant nouns that don’t represent actual sounds
                        if detected_sound.lower() not in ignore_nouns:
                            if buffer:
                                sub_fragments.append(("speech", " ".join(buffer)))
                                buffer = []
                            sub_fragments.append(("sound", detected_sound))
                            print(f"[DEBUG] Detected sound: '{detected_sound}'")

                    elif subtree.label() == "ACTION":
                        detected_action = " ".join(word for word, _ in subtree)

                        # Ensure valid action phrases include key verbs
                        if any(tag.startswith("VB") for _, tag in subtree):
                            if buffer:
                                sub_fragments.append(("speech", " ".join(buffer)))
                                buffer = []
                            sub_fragments.append(("action", detected_action))
                            print(f"[DEBUG] Detected action: '{detected_action}'")

                if buffer:
                    sub_fragments.append(("speech", " ".join(buffer)))

                # Process each sub-fragment inline
                for frag_type, content in sub_fragments:
                    if frag_type == "sound":
                        print(f"[DEBUG] Playing sound for: '{content}'")
                        await self.sound_manager.play_sound_indicator("/home/msutt/hal/sounds/passive/anticipation/n-clong-1.wav")

                    elif frag_type == "action":
                        print(f"[DEBUG] Performing action for: '{content}'")
                        await self.newmovements.tap_all_legs()

                    elif frag_type == "speech":
                        fragment_emotion = self.emotion_handler.analyze_text_emotion(content)
                        emotion_settings = get_voice_modifiers(fragment_emotion)
                        pitch = int(self.baseline_pitch * emotion_settings["pitch_factor"])
                        speed = round(self.baseline_speed * emotion_settings["speed_factor"], 2)

                        print(f"Speaking sub-fragment '{content}' with emotion '{fragment_emotion}': pitch={pitch}, speed={speed}")
                        command = [
                            "flite",
                            "-voice", self.voice_path,
                            "--setf", f"int_f0_target_mean={pitch}",
                            "--setf", f"duration_stretch={speed}",
                            "-t", content,
                        ]
                        await asyncio.to_thread(subprocess.run, command, check=True)

        except Exception as e:
            print(f"Error in adaptive speech, falling back to neutral: {e}")
            await self.speak_with_flite(full_text)
