import os
from robot_hat.utils import get_battery_voltage
from conversation import recognize_speech_vosk, speak_with_flite


# --- Battery Management ---
def get_battery_status():
    """Get the battery voltage and classify the status."""
    voltage = get_battery_voltage()
    if voltage > 7.6:
        return voltage, "Full"
    elif 7.15 <= voltage <= 7.6:
        return voltage, "Medium"
    elif 6.9 <= voltage < 7.15:
        return voltage, "Low"
    else:
        return voltage, "Critical"


def announce_battery_status():
    """Announce the current battery voltage and status."""
    voltage, status = get_battery_status()
    speak_with_flite(f"My battery is currently at {voltage:.2f} volts. Status: {status}.")
    if status == "Low":
        speak_with_flite("Please consider recharging me soon.")
    elif status == "Critical":
        speak_with_flite("Warning! Critical battery level.")


# --- Mode Selection ---  SKIPPING FOR NOW.  STRAIGHT TO CONVERSATION.
def ask_startup_mode():
    """Ask the user to choose the startup mode."""
    speak_with_flite("Hello! What are we doing today? Chat, or Work?")
    retries = 1  # Allow 3 attempts
    for attempt in range(retries):
        mode = recognize_speech_vosk()  # Wait for a spoken response
        if "chat" in mode.lower():
            return "conversation"
        elif "work" in mode.lower():
            return "programming"
        else:
            speak_with_flite(f"I didn't understand.  That was Attempt {attempt + 1} of {retries}. Please say Chat, or Work.")

    # Default to programming mode after retries are exhausted
    speak_with_flite("I couldn't understand. Defaulting to conversation. Standing by for connection.")
    return "conversation"


# --- Modes ---
def start_conversation_mode():
    """Start the conversation mode."""
    speak_with_flite("Starting conversation mode. Please stand by while i test systems!")
    os.system("python3 animated_chat.py")  # Adjust path as needed


def start_programming_mode():
    """Prepare for programming mode."""
    speak_with_flite("Okay, programming it is.")
    # End script without shutting down anything
    return


# --- Main Startup Logic ---
def main():
    """Main entry point for Hal's startup."""
    speak_with_flite("Beginning Startup procedure and Status check.") 
    # Announce battery status
    announce_battery_status()

    # Critical status may be a false alarm during startup depending on timing.
    _, status = get_battery_status()
    if status == "Critical":
        speak_with_flite("Proceed with caution, Imminent shutdown possibility.")

    # Proceed with mode selection
    speak_with_flite("Preparing for conversation mode.")
    start_conversation_mode()
    #mode = ask_startup_mode()
    #if mode == "conversation":
    #    start_conversation_mode()
    ##elif mode == "programming":
    #    start_programming_mode()

if __name__ == "__main__":
    main()
