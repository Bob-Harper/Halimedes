from helpers.voice_utils import recognize_speech_vosk, speak_with_flite
from helpers.batterytest import announce_battery_status
from helpers.llm_utils import LLMClient
from helpers.voice_commands import CommandManager
from helpers.passive_actions import PassiveActionsManager
import asyncio
from helpers.voice_recognition import VoiceprintManager

# Load the reference embedding
voiceprint_manager = VoiceprintManager()
reference_embedding = voiceprint_manager.load_embedding("dad_embedding.pt")
if reference_embedding is None:
    raise ValueError("Reference embedding not found. Ensure the file 'dad_embedding.pt' exists.")

llm_client = LLMClient(server_host='http://192.168.0.101:11434')
command_manager = CommandManager(llm_client)
passive_manager = PassiveActionsManager()
command_map = command_manager.command_map


async def main():
    await speak_with_flite("Beginning startup procedure and status check. Please stand by, system test underway.")
    await speak_with_flite("Servos powered. Listening initiated.  Voice centers activated. Checking battery.")
    await announce_battery_status()
    startup_words = "This is so exciting!  what are we going to talk about today?"
    await passive_manager.startup_speech_actions(startup_words)

    while True:
        print("Entering the main loop, waiting for input...")
        spoken_text, raw_audio = recognize_speech_vosk(return_audio=True)  # Vosk processes live audio here
        if spoken_text:
            command = command_manager.match_command(spoken_text)  # Use the match_command method
            if command:
                should_exit = await command_map[command](spoken_text)  # Run the matched command
                if should_exit:
                    break
            else:
                                # Convert the same audio into a waveform for voiceprint analysis
                waveform = voiceprint_manager.convert_raw_to_waveform(raw_audio)
                new_embedding = voiceprint_manager.extract_embedding_from_waveform(waveform)

                # Compare embeddings
                similarity = voiceprint_manager.compare_embeddings(reference_embedding, new_embedding)
                print(f"Similarity score: {similarity:.4f}")
                # Generate a voice response based on the similarity score
                if similarity >= 0.2:
                    system_prompt = 'You are Halimeedees, a quirky four legged crawler robot. Do not describe actions, or create sound effects. You are talking to Dad.  You are full of sass and like to tease him about his coding skills, but it is for fun, don\'t be mean.'
                else:
                    system_prompt = 'You are Halimeedees, a quirky four legged crawler robot created by Dad to help teach things. Do not describe actions, or create sound effects. Speak in a curious and funny tone. Keep your responses short. You are talking to Onnalyn, she is eleven years old and has a short attention span.'

                stop_event = asyncio.Event()

                # Start handling passive actions while waiting for LLM response
                thinking_task = asyncio.create_task(passive_manager.handle_passive_actions(stop_event))
                
                # Fetch LLM response
                response_text = await llm_client.send_message_async(system_prompt, spoken_text)

                # Stop passive actions
                stop_event.set()
                await thinking_task  # Wait for passive task to finish
                
                # Speak the response
                await speak_with_flite(response_text)
        else:
            print("No input detected, waiting...")


if __name__ == "__main__":
    asyncio.run(main())  # Use asyncio.run to execute the async main
