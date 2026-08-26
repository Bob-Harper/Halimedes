#!/usr/bin/env python3
import gpiozero
from gpiozero import OutputDevice, InputDevice
from crawler.hal_hardware import GPIO_Values as gpio_values
gpio_cfg = gpio_values()

class Pin:
    """
    High-performance native GPIO Controller for Hal.
    All dynamic hardware instance rebuilding and legacy logging leaks are completely purged.
    """


    def __init__(self, pin, mode=0x01, pull=None, *args, **kwargs):
        # Resolve board designation names directly
        self.gpio_values = gpio_cfg
        self.OUT = self.gpio_values.OUT
        self.IN = self.gpio_values.IN

        self.PULL_UP = self.gpio_values.PULL_UP
        self.PULL_DOWN = self.gpio_values.PULL_DOWN
        self.PULL_NONE = self.gpio_values.PULL_NONE

            # Static broadcom dictionary mapping for standard robot hat configuration aliases

        if isinstance(pin, str):
            if pin not in self.gpio_values._dict:
                raise ValueError(f"Pin '{pin}' not found in hardware register specification.")
            self._pin_num = self.gpio_values._dict[pin]
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
