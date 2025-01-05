import asyncio
import time
from robot_hat import TTS
import socket
import json
import speech_recognition as sr


# Initialize recognizer
recognizer = sr.Recognizer()
# Initialize TTS
tts = TTS(engine='espeak')
tts.espeak_params(amp=50, speed=130, gap=2, pitch=40)


def send_to_server(text, source, host='192.168.0.101', port=5000):
    try:
        data = json.dumps({"source": source, "text": text}, ensure_ascii=False)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(data.encode('utf-8'))
            response = s.recv(1024)
        # Decode the JSON response
        response_data = json.loads(response.decode('utf-8'))
        return response_data["response"]
    except Exception as e:
        print(f"Error sending data to server: {e}")
        return None


async def capture_and_transcribe(mic_index):
    tts.lang("en-US")
    try:
        with sr.Microphone(device_index=mic_index) as source:
            print("Adjusting for ambient noise... Please wait.")
            recognizer.adjust_for_ambient_noise(source)
            print("Ready to detect voice...")

            while True:
                # Adjust energy threshold (optional)
                recognizer.energy_threshold = 1000  # Adjust as needed, default is 4000 for Sphinx

                # Async loop for continuous listening
                audio_data = await asyncio.to_thread(recognizer.listen, source, timeout=3)

                if audio_data:
                    print("Detected a voice, listening closely...")

                    # Attempt to recognize speech
                    try:
                        spoken_text = recognizer.recognize_sphinx(audio_data)
                        print(f"spoken_text: {spoken_text}")
                        print("Yep, I heard that. Let me think about it for a minute.")

                        # Send the text to the server and get the response
                        print("Sending transcription to server for processing.")
                        response_text = send_to_server(spoken_text, "Hal")  # Specify "Hal" or "Stygia" as the source

                        if response_text:
                            # Use TTS to speak the response
                            tts.say(response_text)
                            print(f"Response from server: {response_text}")
                            print("Processing complete.")

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
    mic_index = 1  # Change this to the correct device index from the previous script
    asyncio.run(capture_and_transcribe(mic_index))
