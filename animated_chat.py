from voice_utils import recognize_speech_vosk, speak_with_flite
from batterytest import announce_battery_status
from llm_utils import LLMClient
from voice_commands import CommandManager
from passive_actions import PassiveActionsManager
import asyncio

llm_client = LLMClient(server_host='http://192.168.0.101:11434')
command_manager = CommandManager(llm_client)
passive_manager = PassiveActionsManager()
command_map = command_manager.command_map


async def main():
    await speak_with_flite("Servos powered. Listening initiated.  Voice centers activated. Checking battery.")
    await announce_battery_status()
    startup_words = "This is so exciting!  what are we going to talk about today?"
    await passive_manager.startup_speech_actions(startup_words)
    while True:
        spoken_text = recognize_speech_vosk()  # Get input from Vosk
        if spoken_text:
            command = command_manager.match_command(spoken_text)  # Use the match_command method
            if command:
                should_exit = await command_map[command](spoken_text)  # Run the matched command
                if should_exit:
                    break
            else:
                stop_event = asyncio.Event()
                thinking_task = asyncio.create_task(passive_manager.actions_thinking_loop(stop_event))
                system_prompt = 'You are Halimeedees, a quirky alien robot exploring Earth. Speak in a curious and funny tone. Keep your responses short, your audience is young and has a short attention span. Do not use asterisks or actions.'
                response_text = await llm_client.send_message_async(system_prompt, spoken_text)
                stop_event.set()  # Signal the thinking loop to stop
                await thinking_task  # Ensure the thinking task finishes cleanly
                await speak_with_flite(response_text)
        else:
            print("No input detected, waiting...")

if __name__ == "__main__":
    asyncio.run(main())  # Use asyncio.run to execute the async main
