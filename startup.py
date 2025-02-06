from helpers.voice_utils import recognize_speech_vosk, speak_with_flite
from helpers.batterytest import announce_battery_status
from helpers.llm_utils import LLMClient
from helpers.voice_commands import CommandManager
from helpers.passive_actions import PassiveActionsManager
from helpers.voice_recognition import VoiceprintManager
from helpers.emotions import EmotionHandler, EmotionSoundManager
import warnings
import asyncio


warnings.simplefilter('ignore')
# Initialize everything at module level (outside the main() function) as needed:
voiceprint_manager = VoiceprintManager()

# Load all known speaker embeddings here
embeddings = {
    "Dad": voiceprint_manager.load_embedding("dad_embedding.pt"),
    "Onnalyn": voiceprint_manager.load_embedding("onnalyn_embedding.pt"),
    # Add more speakers here as needed
}

threshold = 0.2  # If highest similarity is below this, treat speaker as Unknown.

llm_client = LLMClient(server_host='http://192.168.0.123:11434')  #101 = Stygia, 123 = Studio
emotion_handler = EmotionHandler()
emotion_sound_manager = EmotionSoundManager()

command_manager = CommandManager(llm_client)
passive_manager = PassiveActionsManager()
command_map = command_manager.command_map


async def main():
    await speak_with_flite("Beginning startup procedure and status check. Please stand by, system test underway.")
    await speak_with_flite("Servos powered. Listening initiated. Voice centers activated. Checking battery.")
    await announce_battery_status()

    startup_words = "This is so exciting! What are we going to talk about today?"
    await passive_manager.startup_speech_actions(startup_words)

    while True:
        print("Entering the main loop, waiting for input...")
        spoken_text, raw_audio = await recognize_speech_vosk(return_audio=True)  # Get input and raw audio

        # If no text was recognized, loop back and wait again
        if not spoken_text:
            print("No input detected, waiting...")
            continue

        # Check if input matches a known command
        command = command_manager.match_command(spoken_text)
        if command:
            should_exit = await command_map[command](spoken_text)
            if should_exit:
                break
            continue  # Command handled; go back to listening

        # Otherwise, proceed with normal conversation
        stop_event = asyncio.Event()
        # Detect and play a sound based on user's emotion
        user_emotion = emotion_handler.analyze_text_emotion(spoken_text)
        print(f"Detected user emotion: {user_emotion}")
        emotion_sound_manager.play_sound(user_emotion)

        # 1) Convert raw audio to waveform and extract new embedding
        waveform = voiceprint_manager.convert_raw_to_waveform(raw_audio)
        new_embedding = voiceprint_manager.extract_embedding_from_waveform(waveform)

        # 2) Compare new_embedding to each known speaker
        best_speaker = None
        best_score = -1.0

        for speaker_name, ref_embedding in embeddings.items():
            if ref_embedding is not None:
                similarity = voiceprint_manager.compare_embeddings(new_embedding, ref_embedding)
                if similarity is not None and similarity > best_score:
                    best_score = similarity
                    best_speaker = speaker_name

        # 3) Decide if we have a match or "Unknown"
        if best_score >= threshold:
            recognized_speaker = best_speaker
        else:
            recognized_speaker = "Unknown"

        # 4) Build a system prompt based on recognized_speaker
        if recognized_speaker == "Dad":
            system_prompt = (
                "You are Halimeedees, a quirky four-legged crawler robot. DO NOT describe your actions or sound effects."
                "Multiple humans may speak; keep track of who speaks when by their names. "
                "You are currently talking to Dad. Tease him about his coding skills, "
                "but be playful, not mean. User emotion detected: {user_emotion}."
            )
        elif recognized_speaker == "Onnalyn":
            system_prompt = (
                "You are Halimeedees, a quirky four-legged crawler robot.DO NOT  describe actions or sound effects. "
                "Multiple humans may speak; keep track of them by their names. "
                "You are currently talking to Onnalyn, she is eleven years old and loves cats and snakes and neat robots and watching youtube videos.. "
                "Speak in a curious and funny tone with short answers. User emotion detected: {user_emotion}."
            )
        else:
            system_prompt = (
                "You are Halimeedees, a quirky four-legged crawler robot. "
                "Multiple humans may speak; keep track of them by their names. "
                "This speaker is Unknown. Be friendly and neutral. User emotion detected: {user_emotion}"
            )

        # 5) Label the user input for the model
        user_input_for_llm = f"{recognized_speaker}: {spoken_text}"
        print(f"{recognized_speaker}: {spoken_text}")
        print(f"{recognized_speaker} emotion: {user_emotion}")
        # 6) Handle passive actions while LLM processes
        thinking_task = asyncio.create_task(passive_manager.handle_passive_actions(stop_event))
        response_text = await llm_client.send_message_async(system_prompt, user_input_for_llm)
        stop_event.set()
        await thinking_task  # Wait for background actions to finish

        # Detect Hal's emotion from the response and play the corresponding sound
        hal_emotion = emotion_handler.analyze_text_emotion(response_text)
        print(f"Hal: {response_text}")
        print(f"Hal's emotion: {hal_emotion}")
        emotion_sound_manager.play_sound(hal_emotion)

        # 7) Speak the response
        await speak_with_flite(response_text)


if __name__ == "__main__":
    asyncio.run(main())
