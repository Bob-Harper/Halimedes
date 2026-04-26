# body/hardware_state_manager.py

import os
import psutil
from crawler_utils.utils import get_battery_voltage


class HardwareStateManager:
    def __init__(self):
        self.status = {}

    # ------------------------------
    # BATTERY
    # ------------------------------
    def _get_battery_status(self):
        voltage = get_battery_voltage()

        if voltage <= 0:
            return {
                "voltage": 0,
                "status": "Unknown"
            }

        if voltage > 7.6:
            status = "Full"
        elif 7.15 <= voltage <= 7.6:
            status = "Medium"
        elif 6.9 <= voltage < 7.15:
            status = "Low"
        else:
            status = "Critical"

        return {
            "voltage": voltage,
            "status": status
        }

    # ------------------------------
    # CPU TEMPERATURE
    # ------------------------------
    def _get_cpu_temp_status(self):
        try:
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                temp = int(f.read().strip()) / 1000.0
        except Exception:
            return {
                "temperature": None,
                "status": "Unknown"
            }

        if temp < 50:
            status = "Cool"
        elif temp < 65:
            status = "Warm"
        elif temp < 80:
            status = "Hot"
        else:
            status = "Critical"

        return {
            "temperature": temp,
            "status": status
        }

    # ------------------------------
    # MEMORY
    # ------------------------------
    def _get_memory_status(self):
        mem = psutil.virtual_memory()

        if mem.percent < 60:
            status = "Normal"
        elif mem.percent < 80:
            status = "High"
        else:
            status = "Critical"

        return {
            "available": mem.available,
            "percent": mem.percent,
            "status": status
        }

    # ------------------------------
    # LOAD AVERAGE
    # ------------------------------
    def _get_load_status(self):
        load1, load5, load15 = os.getloadavg()

        # Pi has 4 cores → load1 > 4 means overloaded
        if load1 < 2:
            status = "Normal"
        elif load1 < 4:
            status = "Busy"
        else:
            status = "Overloaded"

        return {
            "load1": load1,
            "load5": load5,
            "load15": load15,
            "status": status
        }

    # ------------------------------
    # UPDATE + SNAPSHOT
    # ------------------------------
    def update(self):
        self.status = {
            "battery": self._get_battery_status(),
            "cpu": self._get_cpu_temp_status(),
            "memory": self._get_memory_status(),
            "load": self._get_load_status(),
        }

    def snapshot(self):
        return dict(self.status)
