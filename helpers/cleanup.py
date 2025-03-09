# helpers/cleanup.py
import sys
from helpers.config import LED_INDICATOR, USR_BUTTON, RST_BUTTON

def cleanup_and_exit():
    """ Clean up GPIO states and exit. """
    print("Cleaning up GPIO and exiting...")
    USR_BUTTON.close()
    RST_BUTTON.close()
    LED_INDICATOR.off()
    sys.exit(0)
