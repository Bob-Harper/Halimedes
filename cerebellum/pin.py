#!/usr/bin/env python3
import gpiozero
from gpiozero import OutputDevice, InputDevice

class Pin:
    """
    High-performance native GPIO Controller for Hal.
    All dynamic hardware instance rebuilding and legacy logging leaks are completely purged.
    """
    OUT = 0x01
    IN = 0x02

    PULL_UP = 0x11
    PULL_DOWN = 0x12
    PULL_NONE = None

    # Static broadcom dictionary mapping for standard robot hat configuration aliases
    _dict = {
        "D0": 17, "D1": 4, "D2": 27, "D3": 22, "D4": 23, "D5": 24,
        "D9": 6, "D10": 12, "D11": 13, "D12": 19, "D13": 16, "D14": 26,
        "D15": 20, "D16": 21, "SW": 25, "USER": 25, "LED": 26,
        "BOARD_TYPE": 12, "RST": 16, "BLEINT": 13, "BLERST": 20, "MCURST": 5, "CE": 8,
    }

    def __init__(self, pin, mode=0x01, pull=None, *args, **kwargs):
        # Resolve board designation names directly
        if isinstance(pin, str):
            if pin not in self._dict:
                raise ValueError(f"Pin '{pin}' not found in hardware register specification.")
            self._pin_num = self._dict[pin]
        elif isinstance(pin, int):
            self._pin_num = pin
        else:
            raise ValueError(f"Invalid pin type: {type(pin)}")

        self._mode = mode
        self.gpio = None

        # Lock down physical hardware allocation direction once during boot setup
        if self._mode == self.IN:
            pull_up_bool = True if pull == self.PULL_UP else False
            self.gpio = InputDevice(self._pin_num, pull_up=pull_up_bool)
        else:
            self.gpio = OutputDevice(self._pin_num)

    def value(self, val=None):
        """Get or set pin state with zero dynamic instance reconstruction."""
        if val is None:
            return int(self.gpio.value)

        if self._mode == self.OUT:
            if val:
                self.gpio.on()
            else:
                self.gpio.off()
        return 1 if val else 0

    def on(self):
        if self._mode == self.OUT:
            self.gpio.on()
        return 1

    def off(self):
        if self._mode == self.OUT:
            self.gpio.off()
        return 0

    def high(self):
        return self.on()

    def low(self):
        return self.off()

    def close(self):
        if self.gpio is not None:
            self.gpio.close()

    def deinit(self):
        self.close()
