import time
import asyncio
from robot_hat import Pin

# Define GPIO Pins
USR_BUTTON = Pin("SW", Pin.IN, Pin.PULL_UP)  # GPIO25 (User Button)
RST_BUTTON = Pin(16, Pin.IN, Pin.PULL_UP)    # GPIO16 (Reset Button)
LED = Pin("LED", Pin.OUT)  # Simulated LED output

# Timing Variables
press_start = None
pressing_usr = False
pressing_rst = False
double_tap_timer = None
usr_double_tap = False
rst_double_tap = False

# Constants
HOLD_DURATION = 3  # Hold time threshold in seconds for actions
DOUBLE_TAP_DELAY = 0.5  # Double-tap max delay (seconds)

# Debug function
def debug_print(msg):
    print(f"[DEBUG] {msg}")

async def monitor_buttons():
    global press_start, pressing_usr, pressing_rst, double_tap_timer, usr_double_tap, rst_double_tap

    while True:
        usr_pressed = USR_BUTTON.value() == 1  # 0 means pressed
        rst_pressed = RST_BUTTON.value() == 1

        # 🟢 **USR Button Handling**
        if usr_pressed and not pressing_usr:
            press_start = time.time()
            pressing_usr = True
            debug_print("USR Button Pressed")
            LED.on()  # Light LED while pressed
            if double_tap_timer and time.time() - double_tap_timer < DOUBLE_TAP_DELAY:
                usr_double_tap = True
                debug_print("USR Button Double-Tapped")

        if not usr_pressed and pressing_usr:
            pressing_usr = False
            LED.off()
            duration = time.time() - press_start
            debug_print(f"USR Button Released after {duration:.2f} sec")
            if usr_double_tap:
                debug_print("🔹 USR Double-Tap Action (Pause/Unpause Hal) 🟡")
                usr_double_tap = False  # Reset flag
            elif duration >= HOLD_DURATION:
                debug_print("🔴 USR Hold Action (Would Kill Hal) 🔴")
            else:
                double_tap_timer = time.time()  # Start double-tap timer

        # 🔴 **RST Button Handling**
        if rst_pressed and not pressing_rst:
            press_start = time.time()
            pressing_rst = True
            debug_print("RST Button Pressed")
            LED.on()
            if double_tap_timer and time.time() - double_tap_timer < DOUBLE_TAP_DELAY:
                rst_double_tap = True
                debug_print("RST Button Double-Tapped")

        if not rst_pressed and pressing_rst:
            pressing_rst = False
            LED.off()
            duration = time.time() - press_start
            debug_print(f"RST Button Released after {duration:.2f} sec")
            if rst_double_tap:
                debug_print("🔹 RST Double-Tap Action (Would Restart Hal) 🔵")
                rst_double_tap = False  # Reset flag
            elif duration >= HOLD_DURATION:
                debug_print("🔴 RST Hold Action (Would Restart Pi) 🔴")
            else:
                double_tap_timer = time.time()  # Start double-tap timer

        # 🟣 **Both Buttons Pressed (Shutdown)**
        if usr_pressed and rst_pressed:
            debug_print("⚡ USR + RST Held Together (Would Shutdown Pi) ⚡")
            LED.on()
            await asyncio.sleep(HOLD_DURATION)
            debug_print("🚨 CONFIRMED: Would Shutdown Pi 🚨")

        await asyncio.sleep(0.1)  # Avoid CPU overload

async def main():
    debug_print("🟢 TEST MODE: Button and LED Simulation Running 🟢")
    await monitor_buttons()

# Run the test script
asyncio.run(main())
