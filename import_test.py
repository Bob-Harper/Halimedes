from flitevox.flite_speaker import FliteSpeaker

def main():
    # Initialize the FliteSpeaker
    speaker = FliteSpeaker()

    # Speak some text
    speaker.speak("I want to sing... SING... SING!!!")

if __name__ == "__main__":
    main()