from body.robot_hat import Motors
import time

motors = Motors(db="./motors_override.db")
motor_id = 1

motors[motor_id].speed(1)
print("[DEBUG] Set LED power to 30%")
time.sleep(3)

motors[motor_id].speed(0.12)
print("[DEBUG] Set LED power to 30%")
time.sleep(3)

motors[motor_id].speed(0)
print("[DEBUG] Set LED power to 30%")
time.sleep(3)
motors[motor_id].speed(5)
print("[DEBUG] Set LED power to 30%")
time.sleep(3)
motors[motor_id].speed(0)
print("[DEBUG] Turned LED OFF")
