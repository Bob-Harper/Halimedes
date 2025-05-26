from body.robot_hat import Motors
import readchar
import time

motors = Motors(db="./motors_override.db")
motor_id = 1  # 2 is also available 
power = 0
enabled = False

def apply_power():
    motors[motor_id].speed(power if enabled else 0)
    state = f"ON @ {power}%" if enabled else "OFF"
    print(f"\n[LED] State: {state}")

print("""
[ LED Spotlight Test - Halimedes Style ]
      Note- effective minimum is 0.12% power
Controls: 
    1-9, 0   = Set brightness (10% to 100%)
    [ ]     = Adjust brightness by 1%
    { }     = Adjust brightness by 0.1%
    , .     = Adjust brightness by 0.01%
    q       = Quit
    SPACE    = Toggle ON/OFF
    CTRL+C   = Quit
""")

try:
    while True:
        key = readchar.readkey().lower()
        if key in '1234567890':
            power = int(key) * 10 if key != '0' else 200
            apply_power()

        elif key == "[":
            power = max(0, power - 1)
            apply_power()
        elif key == "]":
            power = max(0, power + 1)
            apply_power()
        elif key == "{":
            power = max(0, power - 0.1)
            apply_power()
        elif key == "}":
            power = max(0, power + 0.1)
            apply_power()

        elif key == ",":
            power = max(0, power - 0.01)
            apply_power()
        elif key == ".":
            power = max(0, power + 0.01)
            apply_power()

        elif key == ' ':
            enabled = not enabled
            apply_power()
        elif key == "q":
            break
        time.sleep(0.1)

finally:
    print("\n[EXIT] Shutting off LED...")
    motors[motor_id].speed(0)
