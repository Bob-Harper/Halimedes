import time
from RPi import GPIO


IMU_RST_PIN = 17  # Replace with the actual GPIO pin number

GPIO.setmode(GPIO.BCM)
GPIO.setup(IMU_RST_PIN, GPIO.OUT)

def reset_imu():
    GPIO.output(IMU_RST_PIN, GPIO.LOW)
    time.sleep(0.01)   # 10 ms
    GPIO.output(IMU_RST_PIN, GPIO.HIGH)
    time.sleep(0.05)   # 50 ms boot time