import speech_recognition as sr
import sounddevice as sd
import json
from vosk import Model, KaldiRecognizer

def listen_for_sound(mic_index):
    recognizer = sr.Recognizer()
    model = Model("/home/msutt/hal/vosk_models/vosk-model-small-en-us-0.15")
    vosk_recognizer = KaldiRecognizer(model, 16000)

    try:
        print(f"Attempting to use microphone with index {mic_index}")
        # Explicitly set sample rate and channels
        with sr.Microphone(device_index=mic_index, sample_rate=16000) as source:
            print("Adjusting for ambient noise... Please wait.")
            recognizer.adjust_for_ambient_noise(source)
            print("Listening for sound...")
            while True:
                audio = recognizer.listen(source)
                print("I heard that!")

                # Recognizing with Vosk
                if vosk_recognizer.AcceptWaveform(audio.get_raw_data()):
                    result = vosk_recognizer.Result()
                    text = json.loads(result)["text"]
                    if text:
                        print(f"You said: {text}")

    except Exception as e:
        print(f"Error capturing or recognizing audio: {e}")

if __name__ == "__main__":
    mic_index = 1  # Change this to the correct device index
    print(sd.query_devices())
    listen_for_sound(mic_index)
