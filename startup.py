from helpers.voice_utils import recognize_speech_vosk, speak_with_flite
from helpers.batterytest import announce_battery_status
from helpers.llm_utils import LLMClient
from helpers.voice_commands import CommandManager
from helpers.passive_actions import PassiveActionsManager
import asyncio

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
        spoken_text = recognize_speech_vosk()  # Get input from Vosk
        if spoken_text:
            command = command_manager.match_command(spoken_text)  # Use the match_command method
            if command:
                should_exit = await command_map[command](spoken_text)  # Run the matched command
                if should_exit:
                    break
            else:
                stop_event = asyncio.Event()
                system_prompt = 'You are Halimeedees, a quirky four legged crawler robot of unknown origin, you are exploring Earth. Speak in a curious and funny tone. Keep your responses short, your audience is young and has a short attention span. Do not use asterisks or actions.'

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
