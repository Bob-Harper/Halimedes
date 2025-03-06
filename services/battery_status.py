#!/home/msutt/hal/venv/bin/python3
# This is for RPI_MONITOR to output realtime battery status

import time
from robot_hat.utils import get_battery_voltage


def get_battery_status(max_retries=3, retry_delay=2):
    """Retrieve the battery voltage with retries and determine the status."""
    voltage = 0
    for attempt in range(max_retries):
        voltage = get_battery_voltage()
        if voltage > 0:
            break
        time.sleep(retry_delay)

    if voltage <= 0:
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
    return voltage, status


if __name__ == '__main__':
    voltage, status = get_battery_status()
    # Output voltage and status separated by a space.
    # RPi-Monitor will graph the first value and show the second as a label.
    print(f"{voltage:.2f} {status}")
