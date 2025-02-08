from helpers.general_utilities import announce_battery_status, log_response_to_file
import warnings
import asyncio
from helpers.initialization import initialize_system
from helpers.system_prompts import get_system_prompt
components = initialize_system()

warnings.simplefilter('ignore')
# Initialize everything at module level (outside the main() function) as needed:

voiceprint_manager = components["voiceprint_manager"]
llm_client = components["llm_client"]
emotion_handler = components["emotion_handler"]
emotion_sound_manager = components["emotion_sound_manager"]
audio_input = components["audio_input"]
command_manager = components["command_manager"]
actions_manager = components["actions_manager"]
response_manager = components["response_manager"]


async def main():
    await response_manager.speak_with_flite("Beginning startup procedure and status check. Please stand by, system test underway.")
    await response_manager.speak_with_flite("Servos powered. Listening initiated. Voice centers activated. Checking battery.")
    await announce_battery_status()

    startup_words = "This is so exciting! Who am I talking to today?"
    await actions_manager.startup_speech_actions(startup_words)

    while True:
        print("Entering the main loop, waiting for input...")
        spoken_text, raw_audio = await audio_input.recognize_speech_vosk(return_audio=True)  # Get input and raw audio

        # If no text was recognized, loop back and wait again
        if not spoken_text:
            print("No input detected, waiting...")
            continue

        should_exit = await command_manager.handle_command(spoken_text)
        if should_exit:
            break

        # Otherwise, proceed with normal conversation
        stop_event = asyncio.Event()
        # Detect and play a sound based on user's emotion
        user_emotion = emotion_handler.analyze_text_emotion(spoken_text)
        print(f"Detected user emotion: {user_emotion}")
        emotion_sound_manager.play_sound(user_emotion)

        recognized_speaker = voiceprint_manager.recognize_speaker(raw_audio)
        print(f"Recognized speaker: {recognized_speaker}")

        system_prompt = get_system_prompt(recognized_speaker, user_emotion)

        # Label the user input for the model
        user_input_for_llm = f"{recognized_speaker}: {spoken_text}"
        print(f"{recognized_speaker}: {spoken_text}")
        print(f"{recognized_speaker} emotion: {user_emotion}")

        # Handle passive actions while LLM processes
        thinking_task = asyncio.create_task(actions_manager.handle_passive_actions(stop_event))
        response_text = await llm_client.send_message_async(system_prompt, user_input_for_llm)
        stop_event.set()
        await thinking_task  # Wait for background actions to finish

        # Log the response to the file
        log_response_to_file(response_text)

        # Detect Hal's emotion from the response and play the corresponding sound
        hal_emotion = emotion_handler.analyze_text_emotion(response_text)
        print(f"Hal: {response_text}")
        print(f"Hal's emotion: {hal_emotion}")
        emotion_sound_manager.play_sound(hal_emotion)
        # Speak the response
        await response_manager.fully_dynamic_response(response_text)


if __name__ == "__main__":
    asyncio.run(main())
