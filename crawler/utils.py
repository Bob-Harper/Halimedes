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

def run_command(cmd):
    """
    Run a shell command and return (status, output)
    """
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True
        )
        return result.returncode, result.stdout + result.stderr
    except Exception as e:
        return -1, str(e)



def is_installed(cmd):
    """
    Check if command is installed

    :param cmd: command to check
    :type cmd: str
    :return: True if installed
    :rtype: bool
    """
    status, _ = run_command(f"which {cmd}")
    if status in [0, ]:
        return True
    else:
        return False


def mapping(x, in_min, in_max, out_min, out_max):
    """
    Map value from one range to another range

    :param x: value to map
    :type x: float/int
    :param in_min: input minimum
    :type in_min: float/int
    :param in_max: input maximum
    :type in_max: float/int
    :param out_min: output minimum
    :type out_min: float/int
    :param out_max: output maximum
    :type out_max: float/int
    :return: mapped value
    :rtype: float/int
    """
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def get_ip(ifaces=['wlan0', 'eth0']):
    """
    Get IPv4 address for the first interface that has one.
    Returns the IP as a string, or False if none found.
    """
    import socket
    import fcntl
    import struct

    if isinstance(ifaces, str):
        ifaces = [ifaces]

    def _get_iface_ip(iface):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            return socket.inet_ntoa(
                fcntl.ioctl(
                    sock.fileno(),
                    0x8915,  # SIOCGIFADDR
                    struct.pack('256s', iface.encode('utf-8'))
                )[20:24]
            )
        except OSError:
            return None

    for iface in ifaces:
        ip = _get_iface_ip(iface)
        if ip:
            return ip

    return False



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
