#!/usr/bin/env python3
import time
import os
import re
import subprocess
from crawler.pin import Pin
import faulthandler
faulthandler.enable()

def set_volume(value: int):
    value = max(0, min(100, value))
    subprocess.run(
        ["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{value}%"],
        check=False
    )


def reset_mcu():
    """
    Reset mcu on Robot Hat.

    This is helpful if the mcu somehow stuck in a I2C data
    transfer loop, and Raspberry Pi getting IOError while
    Reading ADC, manipulating PWM, etc.
    """
    mcu_reset = Pin("MCURST")
    mcu_reset.off()
    time.sleep(0.01)
    mcu_reset.on()
    time.sleep(0.01)

    mcu_reset.close()


def get_battery_voltage():
    """
    Get battery voltage

    :return: battery voltage(V)
    :rtype: float
    """
    from crawler.adc import ADC
    adc = ADC("A4")
    raw_voltage = adc.read_voltage()
    voltage = raw_voltage * 3
    return voltage
