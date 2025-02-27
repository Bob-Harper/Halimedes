import os
import time
import psutil
from robot_hat import Pin
from robot_hat import I2C


"""
### Updated Feature Set.  KEEP THIS DO NOT REMOVE, IF IT IS REMOVED I WILL CRY.
| Action      | How to Trigger It      | LED Behavior             | Effect
|---------------------------------------------------------------------------------------
| Pause Chat  | Double-tap USR         | Blinks slowly            | Hal pauses chat
| Resume Chat | Double-tap USR again   | Blinking stops, LED OFF  | Hal resumes chat
| Restart Chat| Double-tap RST         | LED pulses while restart | Restarts startup.py
| Exit Chat   | Hold USR for 3 sec     | ON → OFF when unloaded   | Kills chat process
| Restart Pi  | Hold RST for 3 sec     | ON until restarted       | Reboots system
| Shutdown Pi | Hold USR+RST for 3 sec | ON until power off       | Fully shuts down
"""

# Define pins for buttons and LED
USR_BUTTON = Pin("SW", Pin.IN, Pin.PULL_UP)  # GPIO25 (User Button)
RST_BUTTON = Pin(16, Pin.IN, Pin.PULL_UP)    # GPIO16 (Reset Button)
LED = Pin("LED", Pin.OUT)  # Simulated LED output

# Configurable timing settings
HOLD_TIME = 3  # Hold duration for confirming actions
DOUBLE_TAP_TIME = 0.5  # Max time between taps to register as a double-tap
BLINK_INTERVAL = 1.0  # LED blink speed when paused

# Track double-tap timing
last_usr_tap = 0  
last_rst_tap = 0  
hal_paused = False  # ✅ Global pause state

def detect_button_hold(pin):
    """Detects if a button is held for `HOLD_TIME`. Returns True if held long enough, False if released early."""
    start_time = time.time()
    LED.on()  # ✅ LED ON while holding

    while time.time() - start_time < HOLD_TIME:
        if pin.value() == 1:  # 🔥 Fix: Stop checking if released early
            LED.off()  # 🔴 Cancel action if released early
            return False
        time.sleep(0.1)

    return True  # ✅ Confirmation reached

def confirm_process_killed(process_name, timeout=5):
    """Checks if a process is fully terminated before turning off LED."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if not any(process_name in p.name() for p in psutil.process_iter()):
            return True  # ✅ Process is confirmed dead
        time.sleep(0.5)
    return False  # ❌ Process still running after timeout

def toggle_pause_hal():
    """Pauses or resumes Hal's process."""
    global hal_paused

    if hal_paused:
        print("[INFO] Resuming Hal...")
        os.system("pkill -CONT -f startup.py")  # ✅ Resume process
        hal_paused = False
        LED.off()  # ✅ Turn LED off (resume normal)
    else:
        print("[INFO] Pausing Hal...")
        os.system("pkill -STOP -f startup.py")  # ✅ Suspend process
        hal_paused = True
        blink_led_while_paused()

def blink_led_while_paused():
    """Blinks LED every BLINK_INTERVAL seconds to indicate pause mode."""
    while hal_paused:
        LED.on()
        time.sleep(BLINK_INTERVAL)
        LED.off()
        time.sleep(BLINK_INTERVAL)

def restart_hal():
    """Restarts `startup.py`."""
    print("[INFO] Restarting Hal (startup.py)...")
    os.system("pkill -f startup.py")  # ✅ Kill the process
    time.sleep(1)  # Small delay to prevent conflicts
    LED.on()  # ✅ LED ON to indicate restart in progress
    os.system("python3 /home/msutt/hal/startup.py &")  # ✅ Restart Hal
    time.sleep(2)  # Give startup script time to launch
    LED.off()  # ✅ Turn LED off after restart


def is_hat_powered():
    """Checks if the Robot HAT is powered by scanning for its onboard MCU at address 0x14."""
    try:
        i2c_bus = I2C()  # Initialize I2C interface
        devices = i2c_bus.scan()  # Get list of active I2C addresses
        return 0x14 in devices  # ✅ HAT is ON if MCU address 0x14 is found
    except Exception as e:
        print(f"[ERROR] I2C check failed: {e}")
        return False  # Assume HAT is off if there's an error
    

def button_handler():
    """Main loop to handle button presses with LED confirmation & double-tap detection."""
    global last_usr_tap, last_rst_tap  

    while True:
        # 🔥 Check if Robot HAT is powered before reading buttons
        if not is_hat_powered():
            print("[WARNING] Robot HAT is OFF! Ignoring button inputs.")
            LED.off()  # 🔴 Ensure LED is off when HAT is off
            time.sleep(0.5)
            continue  # Skip processing buttons

        usr_pressed = USR_BUTTON.value()
        rst_pressed = RST_BUTTON.value()

        if usr_pressed and rst_pressed:
            print("[DEBUG] Both buttons held: Initiating Shutdown")
            if detect_button_hold(USR_BUTTON) and detect_button_hold(RST_BUTTON):
                print("[INFO] Shutting down system...")
                LED.on()
                os.system("sudo shutdown -h now")
                break

        elif usr_pressed:
            time.sleep(0.05)
            if USR_BUTTON.value() == 0:
                tap_time = time.time()
                if tap_time - last_usr_tap <= DOUBLE_TAP_TIME:
                    print("[INFO] Double-Tap Detected: Pausing/Resuming Hal")
                    toggle_pause_hal()
                    last_usr_tap = 0
                else:
                    last_usr_tap = tap_time
                    time.sleep(DOUBLE_TAP_TIME)

                    if USR_BUTTON.value() == 1:
                        print("[DEBUG] USR button held: Ending Chat Mode")
                        if detect_button_hold(USR_BUTTON):
                            print("[INFO] Killing startup.py...")
                            os.system("pkill -f startup.py")
                            if confirm_process_killed("startup.py"):
                                print("[INFO] startup.py successfully terminated.")
                                LED.off()
                            else:
                                print("[WARNING] startup.py did not exit within timeout.")
                            break

        elif rst_pressed:
            time.sleep(0.05)
            if RST_BUTTON.value() == 1:
                tap_time = time.time()
                if tap_time - last_rst_tap <= DOUBLE_TAP_TIME:
                    print("[INFO] Double-Tap Detected: Restarting Hal")
                    restart_hal()
                    last_rst_tap = 0
                else:
                    last_rst_tap = tap_time
                    time.sleep(DOUBLE_TAP_TIME)

                    if RST_BUTTON.value() == 1:
                        print("[DEBUG] RST button held: Rebooting system")
                        if detect_button_hold(RST_BUTTON):
                            print("[INFO] Rebooting system...")
                            LED.on()
                            os.system("sudo reboot")
                            break

        time.sleep(0.1)  # Prevent CPU overuse

if __name__ == "__main__":
    print("[INFO] Button monitoring started.")
    button_handler()
