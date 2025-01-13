import os
import asyncio
from robot_hat.utils import get_battery_voltage
from voice_utils import speak_with_flite


# --- Battery Management ---
async def get_battery_status():
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


async def announce_battery_status():
    """Announce the current battery voltage and status."""
    voltage, status = await get_battery_status()
    await speak_with_flite(f"My battery is currently at {voltage:.2f} volts. Status: {status}.")
    if status == "Low":
        await speak_with_flite("Please consider recharging me soon.")
    elif status == "Critical":  # Critical status may be a false alarm during startup depending on timing.
        await speak_with_flite("Warning! Critical battery level. Proceed with caution, imminent shutdown possible.")


# --- Main Startup Logic ---
async def main():
    """Main entry point for Hal's startup."""
    await speak_with_flite("Beginning startup procedure and status check.")
    await announce_battery_status()
    await speak_with_flite("Starting conversation mode. Please stand by, system test underway.")
    
    # Start animated_chat.py asynchronously and wait for it
    process = await asyncio.create_subprocess_exec("python3", "animated_chat.py")
    await process.wait()  # This ensures the service waits for the subprocess


if __name__ == "__main__":
    asyncio.run(main())
