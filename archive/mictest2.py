import speech_recognition as sr
import sounddevice as sd


def listen_for_sound(mic_index):
    recognizer = sr.Recognizer()
    try:
        print(f"Attempting to use microphone with index {mic_index}")
        with sr.Microphone(device_index=mic_index) as source:
            print("Adjusting for ambient noise... Please wait.")
            recognizer.adjust_for_ambient_noise(source)
            print("Listening for sound...")
            while True:
                # Listen for audio and save it to the audio variable
                audio = recognizer.listen(source)
                # This will be printed when sound is detected
                print("I heard that!")
                # You can optionally try to recognize the audio here
                try:
                    pass
                except sr.UnknownValueError:
                    print("Could not understand audio")
    except Exception as e:
        print(f"Error capturing or recognizing audio: {e}")

if __name__ == "__main__":
    mic_index = 1  # Change this to the correct device index


# List all available devices
    print(sd.query_devices())
    listen_for_sound(mic_index)
