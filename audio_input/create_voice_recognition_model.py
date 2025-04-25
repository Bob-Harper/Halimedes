#!/home/msutt/hal/.venv/bin/python

import os
import sys
import subprocess

# So Python can find 'helpers' if this script is in /home/msutt/hal/voiceprints:
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
HAL_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
sys.path.append(HAL_ROOT)

from audio_input.voice_recognition_manager import VoiceRecognitionManager


def main():
    print("\n=== Voiceprint Recording & Embedding Utility ===")

    # Prompt for speaker name
    speaker_name = input("Enter speaker name (no spaces, e.g. 'bob' or 'onnalyn'): ").strip()
    if not speaker_name:
        speaker_name = "new_speaker"

    # Prompt for duration
    duration_input = input("How many seconds to record? (default 5): ").strip()
    try:
        duration = int(duration_input)
    except ValueError:
        duration = 5  # fallback default

    # Construct output filenames
    wav_out = os.path.join(SCRIPT_DIR, f"{speaker_name}.wav")
    pt_out = os.path.join(SCRIPT_DIR, f"{speaker_name}.pt")

    print(f"\nWill record for {duration} seconds to {wav_out}")
    print("(Press Ctrl+C to cancel)\n")

    # Record the audio with arecord
    # Adjust -D if needed for your specific mic device
    cmd = [
        "arecord",
        "-D", "plughw:CARD=Device,DEV=0",  # or your known working device
        "-f", "S16_LE",
        "-c", "1",
        "-r", "16000",
        "-d", str(duration),
        wav_out
    ]

    print("** Start speaking now! **")
    subprocess.run(cmd)
    print("\n** Done recording. **")

    # Initialize the VoiceprintManager
    vpm = VoiceRecognitionManager()

    print(f"Extracting embedding from: {wav_out}")
    vpm.save_embedding(wav_out, os.path.basename(pt_out))
    print(f"Saved voiceprint to:      {pt_out}")
    print("\n=== All done! ===\n")


if __name__ == "__main__":
    main()
