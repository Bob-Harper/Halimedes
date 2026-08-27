# crawler/ultrasonic.py
from crawler.pin import Pin
from crawler.pwm import PWM
from crawler.adc import ADC
import time
from crawler.basic import _Basic_class
from typing import Union, List, Tuple, Optional


class Ultrasonic():
    SOUND_SPEED = 343.3 # ms

    def __init__(self, trig, echo, timeout=0.02):
        if not isinstance(trig, Pin):
            raise TypeError("trig must be robot_hat.Pin object")
        if not isinstance(echo, Pin):
            raise TypeError("echo must be robot_hat.Pin object")

        self.timeout = timeout

        trig.close()
        echo.close()
        self.trig = Pin(trig._pin_num)
        self.echo = Pin(echo._pin_num, mode=Pin.IN, pull=Pin.PULL_DOWN)

    def _read(self):
        self.trig.off()
        time.sleep(0.001)
        self.trig.on()
        time.sleep(0.00001)
        self.trig.off()

        pulse_end = 0
        pulse_start = 0
        timeout_start = time.time()
        assert self.echo.gpio is not None
        while self.echo.gpio.value == 0:
            pulse_start = time.time()
            if pulse_start - timeout_start > self.timeout:
                return -1
        while self.echo.gpio.value == 1:
            pulse_end = time.time()
            if pulse_end - timeout_start > self.timeout:
                return -1
        during = pulse_end - pulse_start
        cm = round(during * self.SOUND_SPEED / 2 * 100, 2)
        return cm

    def read(self, times=10):
        for i in range(times):
            a = self._read()
            if a != -1:
                return a
        return -1


class UltrasonicDriver:
    def __init__(self, trig_pin="D2", echo_pin="D3"):
        trig = Pin(trig_pin, mode=Pin.OUT)
        echo = Pin(echo_pin, mode=Pin.IN, pull=Pin.PULL_DOWN)
        self.sensor = Ultrasonic(trig, echo)

    def read_distance(self):
        distance= self.sensor.read()
        # print(f"[UltrasonicDriver] Reading distance: {distance}")
        return distance

    def test_interpret(self, units): # used for test_reflexes in the action_exectuor to test new movements under load by setting them up to trigger as an ultrasonic reflex.
        # print(f"[UltrasonicDriver] Interpreting units: {units}")
        if units is None or units < 0:
            return "NO_ECHO"
        if units <10:
            # print(f"[UltrasonicDriver] BAD_TOUCH: {units}")
            return "BAD_TOUCH"
        return "CLEAR"

    def interpret(self, units):
        test_status = True
        if test_status:
            return "CLEAR" # software disable by setting fixed return vale
        # print(f"[UltrasonicDriver] Interpreting units: {units}")
        if units is None or units < 0:
            return "NO_ECHO"
        if units < 5:
            # print(f"[UltrasonicDriver] BAD_TOUCH: {units}")
            return "BAD_TOUCH"
        if units < 7.5:
            # print(f"[UltrasonicDriver] TOO_CLOSE: {units}")
            return "TOO_CLOSE"
        if units < 15:
            # print(f"[UltrasonicDriver] DANGER: {units}")
            return "DANGER"
        if units < 25:
            return "CAUTION"
        return "CLEAR"

if __name__ == "__main__":
    ultrasonic_driver = UltrasonicDriver(trig_pin="D2", echo_pin="D3")
    while True:
        distance = ultrasonic_driver.read_distance()
        # print(f"Distance: {distance} cm, interpreted as: {ultrasonic_driver.interpret(distance)}")
        time.sleep(0.5)