from body.robot_hat import Motors
import time

motors = Motors(db="./body/motors_override.db")
motor_id = 1

motors[motor_id].speed(100)
time.sleep(0.02)
motors[motor_id].speed(0)
time.sleep(0.25)
motors[motor_id].speed(100)
time.sleep(0.02)
motors[motor_id].speed(0)
time.sleep(0.25)
motors[motor_id].speed(100)
time.sleep(0.02)
motors[motor_id].speed(0)
print("[DEBUG] Turned LED OFF")
