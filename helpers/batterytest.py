import asyncio
from robot_hat.utils import get_battery_voltage
from helpers.voice_utils import speak_with_flite

# --- Battery Management ---
async def get_battery_status(max_retries=3, retry_delay=2):
    """Get the battery voltage with retries and classify the status."""
    for attempt in range(max_retries):
        await speak_with_flite(f"Battery Check {attempt + 1}.")
        voltage = get_battery_voltage()
        if voltage > 0:
            break
        await asyncio.sleep(retry_delay)

    if voltage <= 0:  # Still 0 after retries
        voltage = 0
        status = "Unknown"
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
        await speak_with_flite("Please monitor power levels closely and consider power pack recharge.")
    elif status == "Critical": 
        await speak_with_flite("Warning! Immediate power pack recharge recommended, imminent shutdown possibility..")
    elif status == "Unknown":  # Checking battery too early after startup may return no result
        await speak_with_flite("Proceed with caution, recheck battery status regularly, consider a hardware status check.")

