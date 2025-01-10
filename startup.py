import os
from robot_hat.utils import get_battery_voltage
from voice_utils import reset_microphone, recognize_speech_vosk, speak_with_flite


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
        speak_with_flite("Warning! Critical battery level. I may shut down soon.")


# --- Mode Selection ---
def ask_startup_mode():
    """Ask the user to choose the startup mode."""
    speak_with_flite("Hello! What are we doing today? Chat, or Code?")
    retries = 3  # Allow 3 attempts
    for attempt in range(retries):
        mode = recognize_speech_vosk()  # Wait for a spoken response
        if "chat" in mode.lower():
            return "conversation"
        elif "code" in mode.lower():
            return "programming"
        else:
            speak_with_flite(f"I didn't understand. Please say Chat, or Code. Attempt {attempt + 1} of {retries}.")

    # Default to programming mode after retries are exhausted
    speak_with_flite("I couldn't understand. Defaulting to programming mode.")
    return "programming"


# --- Modes ---
def start_conversation_mode():
    """Start the conversation mode."""
    speak_with_flite("Starting conversation mode. Let's chat!")
    os.system("python3 conversation.py")  # Adjust path as needed


def start_programming_mode():
    """Prepare for programming mode."""
    speak_with_flite("Okay, programming it is.")
    # End script without shutting down anything
    return


# --- Main Startup Logic ---
def main():
    """Main entry point for Hal's startup."""
    # Announce battery status
    announce_battery_status()

    # Check battery status and act accordingly
    _, status = get_battery_status()
    if status == "Critical":
        speak_with_flite("Battery too low to continue. Shutting down.")
        return  # Exit program to conserve power

    # Proceed with mode selection

    mode = ask_startup_mode()
    if mode == "conversation":
        start_conversation_mode()
    elif mode == "programming":
        start_programming_mode()

if __name__ == "__main__":
    reset_microphone() 
    main()
