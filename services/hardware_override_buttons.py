import signal
import sys
import os
from gpiozero import Button, LED, DigitalInputDevice

# GPIO Setup
USR_BUTTON = Button(25, pull_up=True, bounce_time=0.1)  # User Button
RST_BUTTON = Button(16, pull_up=True, bounce_time=0.1)  # Reset Button
LED_INDICATOR = LED(26)  # LED
HAT_STATUS = DigitalInputDevice(12, pull_up=False)  # GPIO12 detects Hat power

# Constants
HOLD_DURATION = 3  # Seconds for hold actions
DOUBLE_TAP_DELAY = 0.5  # Seconds for double-tap detection


def cleanup_and_exit(signum, frame):
    HAT_STATUS.close()  # Release GPIO12
    USR_BUTTON.close()
    RST_BUTTON.close()
    LED_INDICATOR.off()
    sys.exit(0)


# Handle Ctrl+C and termination signals
signal.signal(signal.SIGINT, cleanup_and_exit)
signal.signal(signal.SIGTERM, cleanup_and_exit)


# Function to check if the Hat is ON/OFF
def is_hat_on():
    return HAT_STATUS.value  # Returns True if Hat is ON


def usr_pressed():
    if is_hat_on():
        LED_INDICATOR.on()
    else:
        LED_INDICATOR.off()


def rst_pressed():
    if is_hat_on():
        LED_INDICATOR.off()
    else:
        LED_INDICATOR.on()


def usr_released():
    if is_hat_on():
        LED_INDICATOR.off()
    else:
        LED_INDICATOR.on()
    os.system("sudo systemctl stop hal_startup.service")  # Actually stop Hal    


def rst_released():
    if is_hat_on():
        LED_INDICATOR.off()
    else:
        LED_INDICATOR.on()
    os.system("sudo shutdown -h now")  # Actually shut down    


# Assign button functions
USR_BUTTON.when_pressed = usr_pressed
USR_BUTTON.when_released = usr_released
RST_BUTTON.when_pressed = rst_pressed
RST_BUTTON.when_released = rst_released

# Start monitoring buttons
from signal import pause
pause()