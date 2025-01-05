import asyncio
from time import sleep
import speech_recognition as sr
from classes.llm_communicator import LLMCommunicator  # Send to AI LLM model and speak result
from classes.new_movements import NewMovements  # New movements not in Picrawler
from classes.picrawler import Picrawler  # Robot movement library
from classes.tts import TTS  # for audio updates
from vilib import Vilib

# Initialize recognizer
recognizer = sr.Recognizer()
flag_face = False


class RobotController:
    def __init__(self, host='192.168.0.101', port=5000):
        self.llm = LLMCommunicator(host, port)
        self.picrawler = Picrawler()
        self.tts = TTS()
        self.new_moves = NewMovements(self.picrawler)  # Pass picrawler instance to NewMovements

    async def capture_and_transcribe(self, mic_index, speed):
        global flag_face
        try:
            await self.tts.say_async("Is there anybody out there?")  # Using async say method
            recognizer.energy_threshold = 800  # Adjust as needed, default is 4000 for Sphinx

            while True:
                # Listen for initial audio input
                with sr.Microphone(device_index=mic_index) as source:
                    initial_audio_data = await asyncio.to_thread(recognizer.listen, source, timeout=3)

                if initial_audio_data:
                    print("Detected a voice, looking for the speaker...")

                    # Robot hears initial speech
                    await self.tts.say_async("I heard that!")
                    Vilib.face_detect_switch(True)  # Turn on face detection
                    Vilib.camera_start(vflip=False, hflip=False)
                    Vilib.display(local=True, web=False)
                    # Start looking for the speaker's face
                    while True:
                        if 'human_n' in Vilib.detect_obj_parameter and Vilib.detect_obj_parameter['human_n'] > 0:
                            print('Face Detected')
                            await self.tts.say_async("There you are. Now, what do you have to say for yourself?")

                            # Listen for new audio input after detecting the face
                            with sr.Microphone(device_index=mic_index) as source:
                                response_audio_data = await asyncio.to_thread(recognizer.listen, source, timeout=5)

                            if response_audio_data:
                                spoken_text = recognizer.recognize_sphinx(response_audio_data)
                                # Handle the spoken text
                                print(f"Recognized text: {spoken_text}")

                                # Continue with the rest of the code using the recognized text
                                await self.picrawler.do_step_async('stand', 1, speed)
                                await self.new_moves.stand_tall_async()

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
                        else:
                            print('No face detected, continuing to search...')
                            await self.new_moves.look_left_async()  # Assume this is an async method that makes the robot turn left
                            await asyncio.sleep(1)  # Small delay to simulate turning and checking

                else:
                    print("No audio input detected. Waiting...")

                # Add a short delay to prevent continuous CPU utilization
                await asyncio.sleep(0.1)

        except sr.UnknownValueError:
            print("Sphinx could not understand the audio")
        except sr.RequestError as e:
            print(f"Could not request results from Sphinx service; {e}")
        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    speed = 80
    mic_index = 1  # Change this to the correct device index
    robot_controller = RobotController(host='192.168.0.101', port=5000)  # Uses default host and port
    asyncio.run(robot_controller.capture_and_transcribe(mic_index, speed))
