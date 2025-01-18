import asyncio
from helpers.voice_utils import speak_with_flite

# Flag to prevent re-launching animated_chat.py
is_chat_started = False

# --- Main Startup Logic ---
async def main():
    """Main entry point for Hal's startup."""
    global is_chat_started
    if not is_chat_started:
        await speak_with_flite("Beginning startup procedure and status check. Please stand by, system test underway.")
        await speak_with_flite("Preparing for conversation mode. ")
        process = await asyncio.create_subprocess_exec("python3", "animated_chat.py")
        is_chat_started = True  # Set flag to indicate chat has started
        await process.wait()  # Wait until animated_chat finishes
    else:
        # If chat has already ended, announce that the system is now in standby
        await speak_with_flite("Chat has ended. I am now in standby mode.")


if __name__ == "__main__":
    asyncio.run(main())
