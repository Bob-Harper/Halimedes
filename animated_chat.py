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
    await speak_with_flite("Servos powered. Listening initiated.  Voice centers activated. Double checking battery.")
    await announce_battery_status()
    startup_words = "This is so exciting!  what are we going to talk about today?"
    await passive_manager.startup_speech_actions(startup_words)
    while True:
        spoken_text = recognize_speech_vosk()  # Get input from Vosk
        if spoken_text:
            command = spoken_text.lower().strip()  # Normalize input
            
            if command in command_map:
                # Call the corresponding command function
                should_exit = await command_map[command](spoken_text)  # Await the function and check return value
                if should_exit:  # If the command has "return True", ends the script
                    break
            else:
                # Perform thinking variations while waiting for LLM
                thinking_task = asyncio.create_task(passive_manager.actions_thinking())                
                response_text = await llm_client.send_message_async(spoken_text)
                await thinking_task  # Wait for thinking to finish if still running
                await speak_with_flite(response_text)
        else:
            print("No input detected, waiting...")

if __name__ == "__main__":
    asyncio.run(main())  # Use asyncio.run to execute the async main
