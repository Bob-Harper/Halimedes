import asyncio
from helpers.voice_utils import recognize_speech_vosk, speak_with_flite
from helpers.voice_recognition import VoiceprintManager

# Initialize VoiceprintManager
voiceprint_manager = VoiceprintManager()

# Load the reference embedding
reference_embedding = voiceprint_manager.load_embedding("dad_embedding.pt")
if reference_embedding is None:
    raise ValueError("Reference embedding not found. Ensure the file 'dad_embedding.pt' exists.")

async def main():
    print("Halimedes is ready to listen for voice input...")
    await speak_with_flite("I'm listening now. Speak whenever you're ready.")

    while True:
        print("Listening for speech...")
        spoken_text, raw_audio = recognize_speech_vosk(return_audio=True)  # Vosk processes live audio here
        if spoken_text:
            print(f"Detected speech: {spoken_text}")

            # Convert the same audio into a waveform for voiceprint analysis
            print("Processing waveform for voiceprint analysis...")
            waveform = voiceprint_manager.convert_raw_to_waveform(raw_audio)
            new_embedding = voiceprint_manager.extract_embedding_from_waveform(waveform)
            print("New embedding extracted successfully!")

            # Compare embeddings
            similarity = voiceprint_manager.compare_embeddings(reference_embedding, new_embedding)
            print(f"Similarity score: {similarity:.4f}")

            # Generate a voice response based on the similarity score
            if similarity >= 0.2:
                response = f"Hello, Dad! I heard you say: {spoken_text}"
            else:
                response = f"I didn't recognize the speaker, but here's what I heard: {spoken_text}"

            print(f"Response: {response}")
            await speak_with_flite(response)
        else:
            print("No speech detected.")

if __name__ == "__main__":
    asyncio.run(main())
