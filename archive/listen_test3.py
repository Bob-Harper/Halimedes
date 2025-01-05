import asyncio
from time import sleep
import speech_recognition as sr
from classes.llm_communicator import LLMCommunicator  # Send to AI LLM model and speak result
from classes.new_movements import NewMovements  # New movements not in Picrawler
from classes.picrawler import Picrawler  # Robot movement library
from robot_hat import TTS  # for audio updates

# Initialize recognizer
recognizer = sr.Recognizer()

class RobotController:
    def __init__(self, host='192.168.0.101', port=5000):
        self.llm = LLMCommunicator(host, port)
        self.picrawler = Picrawler()
        self.tts = TTS()
        self.new_moves = NewMovements(self.picrawler)  # Pass picrawler instance to NewMovements

    async def capture_and_transcribe(self, mic_index, speed):
        try:
            with sr.Microphone(device_index=mic_index) as source:
                print("Adjusting for ambient noise... Please wait.")
                recognizer.adjust_for_ambient_noise(source)
                print("Ready to detect voice...")
                self.tts.say("Is there anybody out there?")
                while True:
                    # Adjust energy threshold (optional)
                    recognizer.energy_threshold = 800  # Adjust as needed, default is 4000 for Sphinx

                    # Async loop for continuous listening
                    audio_data = await asyncio.to_thread(recognizer.listen, source, timeout=3)

                    if audio_data:
                        print("Detected a voice, listening closely...")
                        self.new_moves.look_left()
                        self.new_moves.look_right()
                        self.new_moves.look_right()
                        self.new_moves.look_left()
                        self.tts.say("I heard that!")  # say I Heard That and do recognizer while doing look movements
                        self.picrawler.do_step('stand', 1, speed)
                        # Attempt to recognize speech
                        try:
                            spoken_text = recognizer.recognize_sphinx(audio_data)
                            print(f"spoken_text: {spoken_text}")

                            self.tts.say("Wait Right There.")
                            self.picrawler.do_action('wave', 1, speed)  # Async to tap while speaking the "Wait Right There."?
                            self.tts.say("Thinking.")
                            self.new_moves.tap_front_right()  # Async to action while speaking
                            # Send the text to the server and get the response
                            print("Sending transcription to server for processing.")
                            self.tts.say("This is going to take me a moment.")
                            self.new_moves.tap_all_legs()
                            self.new_moves.tap_all_legs()
                            self.new_moves.tap_all_legs()
                            response_text = self.llm.get_response(spoken_text)  # Async to move legs while generating text but WAIT FOR ACTION TO COMPLETE then speak
                            self.tts.say(response_text)
                            print("Processing complete.")
                            self.new_moves.sit_down()
                            # Break the loop after processing one input
                            break

                        except sr.UnknownValueError:
                            print("Sphinx could not understand the audio")
                        except sr.RequestError as e:
                            print(f"Could not request results from Sphinx service; {e}")
                        except Exception as e:
                            print(f"Error processing speech: {e}")

                    else:
                        print("No audio input detected. Waiting...")

                    # Add a short delay to prevent continuous CPU utilization
                    await asyncio.sleep(0.1)

        except Exception as e:
            print(f"Error capturing or recognizing audio: {e}")

if __name__ == "__main__":
    speed = 80
    mic_index = 1  # Change this to the correct device index
    robot_controller = RobotController(host='192.168.0.101', port=5000)  # Uses default host and port
    asyncio.run(robot_controller.capture_and_transcribe(mic_index, speed))
