from robot_hat import Pin
import time

# Define pins for buttons and LED
USR_BUTTON = Pin("SW", Pin.IN, Pin.PULL_UP)  # GPIO25 (User Button)
RST_BUTTON = Pin(16, Pin.IN, Pin.PULL_UP)    # GPIO16 (Reset Button)
LED = Pin("LED", Pin.OUT)  # Simulated LED output (DO NOT READ FROM IT)

print("Press and release buttons. Observe changes.")

while True:
    usr_state = USR_BUTTON.value()
    rst_state = RST_BUTTON.value()

    print(f"USR: {usr_state}, RST: {rst_state}")

    # Simulate LED response to USR Button
    if usr_state == 1:  
        LED.on()  # ✅ LED turns ON when USR is pressed
    else:
        LED.off()  # ✅ LED turns OFF when USR is released

    time.sleep(1)
