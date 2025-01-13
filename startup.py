import asyncio
from robot_hat.utils import get_battery_voltage
from voice_utils import speak_with_flite


# --- Battery Management ---
async def get_battery_status(max_retries=5, retry_delay=2):
    """Get the battery voltage with retries and classify the status."""
    for attempt in range(max_retries):
        await speak_with_flite(f"Battery Check {attempt + 1}.")
        voltage = get_battery_voltage()
        if voltage > 0:
            break
        await asyncio.sleep(retry_delay)

    if voltage <= 0:  # Still 0 after retries
        voltage = 0
        status = "Critical"
    else:
        if voltage > 7.6:
            status = "Full"
        elif 7.15 <= voltage <= 7.6:
            status = "Medium"
        elif 6.9 <= voltage < 7.15:
            status = "Low"
        else:
            status = "Critical"

    # Log the voltage and status
    return voltage, status


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
    await speak_with_flite("Beginning startup procedure and status check. Please stand by, system test underway.")
    await announce_battery_status()
    await speak_with_flite("Preparing for conversation mode. ")
    
    # Start animated_chat.py asynchronously and wait for it
    process = await asyncio.create_subprocess_exec("python3", "animated_chat.py")
    await process.wait()  # This ensures the service waits for the subprocess


if __name__ == "__main__":
    asyncio.run(main())
