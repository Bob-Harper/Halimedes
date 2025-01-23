import torch
import torchaudio
import sounddevice as sd
import numpy as np
from helpers.voice_recognition import VoiceprintManager

# Initialize VoiceprintManager
voiceprint_manager = VoiceprintManager()
reference_file = "dad_embedding.pt"  # Adjust path as needed

try:
    # Load the reference embedding
    print("Loading reference embedding...")
    reference_embedding = voiceprint_manager.load_embedding(reference_file)
    print("Reference embedding loaded successfully!")
except Exception as e:
    print(f"Error loading reference embedding: {e}")
    exit(1)

try:
    # Listen to microphone input
    print("Listening for 5 seconds...")
    device_index = 1  # Ensure this matches your microphone index
    duration = 10  # seconds

    with sd.RawInputStream(samplerate=44100, blocksize=8000, dtype="int16",
                           channels=1, device=device_index) as stream:
        print("Recording audio...")
        raw_audio = stream.read(int(44100 * duration))[0]
        print("Audio captured successfully!")

    # Convert raw audio to waveform
    print("Processing audio into waveform...")
    waveform = torch.tensor(np.frombuffer(raw_audio, dtype=np.int16), dtype=torch.float32).unsqueeze(0)
    waveform = waveform / 32768.0  # Normalize to [-1, 1]
    if waveform.dim() == 2:
        waveform = waveform.unsqueeze(1)
    print(f"Waveform shape: {waveform.shape}")

    # Ensure proper sampling rate
    print("Resampling audio to 16 kHz...")
    waveform = torchaudio.transforms.Resample(orig_freq=44100, new_freq=16000)(waveform)

    # Extract embedding for the new audio
    print("Extracting embedding from waveform...")
    new_embedding = voiceprint_manager.extract_embedding_from_waveform(waveform)
    print("New embedding extracted successfully!")

    # Compare embeddings
    print("Comparing embeddings...")
    similarity = voiceprint_manager.compare_embeddings(reference_embedding, new_embedding)
    print(f"Similarity score: {similarity:.4f}")

except Exception as e:
    print(f"Error during audio processing or embedding extraction: {e}")

finally:
    print("Finished processing audio.")
