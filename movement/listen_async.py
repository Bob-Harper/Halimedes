import asyncio
from time import sleep
import speech_recognition as sr
from classes.llm_communicator import LLMCommunicator  # Send to AI LLM model and speak result
from classes.new_movements import NewMovements  # New movements not in Picrawler
from classes.picrawler import Picrawler  # Robot movement library
from classes.ttsflitevox import TTS  # for audio updates

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
                await self.tts.say_async("Is there anybody out there?")  # Using async say method
                while True:
                    # Adjust energy threshold (optional)
                    recognizer.energy_threshold = 800  # Adjust as needed, default is 4000 for Sphinx

                    # Async loop for continuous listening
                    audio_data = await asyncio.to_thread(recognizer.listen, source, timeout=3)

                    if audio_data:
                        print("Detected a voice, listening closely...")

                        # Attempt to recognize speech
                        try:

                            # Robot hears speech
                            await self.new_moves.look_left_async()
                            await self.new_moves.look_right_async()
                            # Robot speaks while looking around
                            await self.tts.say_async("I heard that!")
                            await self.new_moves.look_right_async()
                            await self.new_moves.look_left_async()
                            spoken_text = recognizer.recognize_sphinx(audio_data)
                            # Wait for looking around and speaking to complete
                            await self.picrawler.do_step_async('stand', 1, speed)
                            await self.new_moves.stand_tall_async()

                            print(f"spoken_text: {spoken_text}")

                            # Robot waves while speaking "Wait Right There"
                            wave_task = asyncio.create_task(self.picrawler.do_action_async('wave', 1, speed))
                            await self.tts.say_async("Wait Right There")
                            await wave_task

                            # Robot taps front right leg while saying "Thinking"
                            tap_task = asyncio.create_task(self.new_moves.tap_front_right_async())
                            await self.tts.say_async("Thinking")
                            await tap_task

                            # Send text to the server for processing
                            print("Sending transcription to server for processing.")
                            # Robot taps all legs while saying "This is going to take me a moment"
                            tap_all_task = asyncio.create_task(self.new_moves.tap_all_legs_async())
                            say_task = asyncio.create_task(self.tts.say_async("This is going to take me a moment"))
                            response_text = await self.llm.get_response_async(spoken_text)
                            await asyncio.gather(tap_all_task, say_task)

                            # Robot speaks the response
                            await self.tts.say_async(response_text)
                            print(f"response_text: {response_text}")
                            print("Processing complete.")

                            # Robot sits down
                            await self.new_moves.sit_down_async()

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
