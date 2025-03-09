import os
import time
from robot_hat import Pin

# Define pins for buttons and LED
USR_BUTTON = Pin(25, Pin.IN, Pin.PULL_UP)
RST_BUTTON = Pin(16, Pin.IN, Pin.PULL_UP)
LED = Pin("LED", Pin.OUT)

HOLD_TIME = 3  # Hold duration for confirming actions

def detect_button_hold(pin):
    """Detects if a button is held for `HOLD_TIME`. Returns True if held long enough, False if released early."""
    start_time = time.time()
    LED.on()  # LED ON while holding

    initial_value = pin.value()

    while time.time() - start_time < HOLD_TIME:
        if pin.value() != initial_value:  # Button released early
            LED.off()
            return False
        time.sleep(0.1)

    print(f"[DEBUG] {pin} hold confirmed at {HOLD_TIME} sec! Action triggered.")
    LED.off()
    return True  # Confirmation reached

def button_listener():
    """Listens for button events in a non-blocking loop."""
    print("[INFO] Button monitoring started. Waiting for button events...")

    while True:
        usr_pressed = USR_BUTTON.value()
        rst_pressed = RST_BUTTON.value()

        if usr_pressed and rst_pressed:
            print("[DEBUG] Both buttons pressed")
            if detect_button_hold(USR_BUTTON) and detect_button_hold(RST_BUTTON):
                print("[DEBUG] Both buttons held: Initiating Shutdown")
                LED.on()
                # os.system("sudo shutdown -h now")  # Uncomment to enable shutdown

        elif usr_pressed:
            print("[DEBUG] USR button pressed.")
            if detect_button_hold(USR_BUTTON):
                print("[DEBUG] USR_BUTTON held: Shutting down startup.py")
                LED.on()
                # os.system("sudo systemctl stop hal_startup.service")  # Uncomment to enable shutdown

        elif rst_pressed:
            print("[DEBUG] RST button pressed.")
            if detect_button_hold(RST_BUTTON):
                print("[DEBUG] RST button held: Rebooting system")
                LED.on()
                # os.system("sudo reboot")  # Uncomment to enable reboot

        time.sleep(0.1)  # Prevent CPU overuse

if __name__ == "__main__":
    button_listener()
