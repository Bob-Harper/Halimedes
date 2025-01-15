import asyncio
import subprocess

# Default settings
pitch = 100
speed = 1.0
test_phrase = "This is a test of my speech capabilities."
voice_path = "/home/msutt/hal/flitevox/cmu_us_rms.flitevox"  # Default voice file

# Voice options
voices = [
    {"name": "Andro", "file": "cmu_us_rxr.flitevox", "description": "Deeper, could be any gender"},
    {"name": "Indian Girl", "file": "cmu_us_axb.flitevox", "description": "Indian girl"},
    {"name": "Scottish with Static", "file": "cmu_us_clb.flitevox", "description": "Sort of Scottish but has a static burst at the start"},
    {"name": "Faint Scottish", "file": "cmu_us_eey.flitevox", "description": "Very faint Scottish, good thought for Stygia"},
    {"name": "Scottish Siri 1", "file": "cmu_us_ljm.flitevox", "description": "Scottish Siri"},
    {"name": "Scottish Siri 2", "file": "cmu_us_slt.flitevox", "description": "More Scottish Siri"},
    {"name": "Stephen Hawking", "file": "cmu_us_aew.flitevox", "description": "Stephen Hawking"},
    {"name": "Deeper Male", "file": "cmu_us_ahw.flitevox", "description": "Deeper, slightly Scottish"},
    {"name": "Higher Male", "file": "cmu_us_aup.flitevox", "description": "Higher pitch, slight Scottish"},
    {"name": "Scottish Hawking", "file": "cmu_us_awb.flitevox", "description": "Scottish Stephen Hawking"},
    {"name": "Natural Male", "file": "cmu_us_bdl.flitevox", "description": "More natural Stephen Hawking"},
    {"name": "Deeper Male 2", "file": "cmu_us_fem.flitevox", "description": "Deeper basic male"},
    {"name": "Quiet Scottish", "file": "cmu_us_gka.flitevox", "description": "Stronger Scottish, quiet volume"},
    {"name": "Deeper Quieter Male", "file": "cmu_us_jmk.flitevox", "description": "Deeper, softer, quieter"},
    {"name": "Scottish/Indian", "file": "cmu_us_ksp.flitevox", "description": "Much stronger Scottish/Indian"},
    {"name": "Default RMS", "file": "cmu_us_rms.flitevox", "description": "Slower, deeper (default)"},
]

# Voice selection helper
def select_voice():
    global voice_path
    print("\nAvailable Voice Files:")
    for i, voice in enumerate(voices, start=1):
        print(f"{i}. {voice['name']} - {voice['description']}")
    print("Type 'cancel' to return to the main menu.")
    while True:
        choice = input("Choose a voice file (1-16): ").strip()
        if choice.lower() == "cancel":
            break
        if choice.isdigit() and 1 <= int(choice) <= len(voices):
            selected_voice = voices[int(choice) - 1]
            voice_path = f"/home/msutt/hal/flitevox/{selected_voice['file']}"
            print(f"Selected voice: {selected_voice['name']} ({selected_voice['description']})")
            break
        else:
            print("Invalid choice. Please select a valid option.")

# Speech function
async def speak_with_flite(phrase, pitch, speed, voice_path):
    """Speak the given phrase with specified pitch, speed, and voice file using Flite."""
    try:
        command = [
            "flite",
            "-voice", voice_path,
            "--setf", f"int_f0_target_mean={pitch}",
            "--setf", f"duration_stretch={speed}",
            "-t", phrase,
        ]
        await asyncio.to_thread(subprocess.run, command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error speaking: {e}")
    except FileNotFoundError:
        print("Flite command not found. Ensure it is installed and in the PATH.")

# Main test function
async def test_speech():
    global pitch, speed, test_phrase, voice_path

    while True:
        print(f"\nCurrent Test Phrase: \"{test_phrase}\"")
        print(f"Current Pitch: {pitch}, Current Speed: {speed}, Current Voice: {voice_path.split('/')[-1]}")
        print("Options:")
        print("1. Update test phrase")
        print("2. Adjust pitch")
        print("3. Adjust speed")
        print("4. Select voice file")
        print("5. Speak with current settings")
        print("Type 'quit' to exit.")
        choice = input("Choose an option (1-5): ").strip()

        if choice == "1":
            test_phrase = input("Enter the new test phrase: ").strip()
        elif choice == "2":
            try:
                pitch = float(input("Enter the new pitch (default: 100): ").strip())
            except ValueError:
                print("Invalid input. Pitch remains unchanged.")
        elif choice == "3":
            try:
                speed = float(input("Enter the new speed (default: 1.0): ").strip())
            except ValueError:
                print("Invalid input. Speed remains unchanged.")
        elif choice == "4":
            select_voice()
        elif choice == "5":
            print(f"Speaking with pitch={pitch}, speed={speed}, voice={voice_path.split('/')[-1]}...")
            await speak_with_flite(test_phrase, pitch, speed, voice_path)
        elif choice.lower() == "quit":
            print("Exiting test program. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    asyncio.run(test_speech())
