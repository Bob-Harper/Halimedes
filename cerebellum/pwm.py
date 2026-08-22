# cerebellum/pwm.py
#!/usr/bin/env python3
import math
from cerebellum.i2c import I2C
from crawler.hal_hardware import PWM_Values

class PWM(I2C):
    """
    High-performance native Python PWM driver interface.
    Natively references your isolated PWM_Values specification block.
    """
    def __init__(self, channel, address=None, *args, **kwargs):
        self.hw = PWM_Values()

        target_addr = address if address is not None else self.hw.PWM_ADDR
        super().__init__(target_addr, *args, **kwargs)

        if isinstance(channel, str):
            if channel.startswith("P"):
                channel = int(channel[1:])
            else:
                raise ValueError(f'PWM channel should be between [P0, P15], not "{channel}"')

        if channel > 15 or channel < 0:
            raise ValueError(f'Channel must be in range of 0-15, not "{channel}"')

        self.channel = channel
        self.timer_group = int(channel / 4)

        self._pulse_width = 0
        self._pulse_width_percent = 0.0
        self._freq = self.hw.PWM_DEFAULT_FREQ
        self._prescaler = 1
        self._arr = 1

        self.freq(self.hw.PWM_DEFAULT_FREQ)

    def _i2c_write_word(self, reg, value):
        """
        Natively channels big-endian word data parameters into
        the explicit I2C register memory address slot.
        """
        val_h = (value >> 8) & 0xFF
        val_l = value & 0xFF

        # Passes the payload block and targeted memory address cleanly
        self.mem_write([val_h, val_l], reg)


    def freq(self, freq_hz=None):
        if freq_hz is None:
            return self._freq

        self._freq = int(freq_hz)
        total_divider = self.hw.PWM_CLOCK / self._freq

        self._prescaler = round(math.sqrt(total_divider))
        self._arr = round(total_divider / self._prescaler)

        self._i2c_write_word(self.hw.REG_PWM_PSC + self.timer_group, self._prescaler - 1)
        self._i2c_write_word(self.hw.REG_PWM_ARR + self.timer_group, self._arr)
        return self._freq

    def prescaler(self, psc_val=None):
        if psc_val is None:
            return self._prescaler
        self._prescaler = round(psc_val)
        self._freq = self.hw.PWM_CLOCK / (self._prescaler * self._arr)
        self._i2c_write_word(self.hw.REG_PWM_PSC + self.timer_group, self._prescaler - 1)
        return self._prescaler

    def period(self, arr_val=None):
        if arr_val is None:
            return self._arr
        self._arr = round(arr_val)
        self._freq = self.hw.PWM_CLOCK / (self._prescaler * self._arr)
        self._i2c_write_word(self.hw.REG_PWM_ARR + self.timer_group, self._arr)
        return self._arr

    def pulse_width(self, width_val=None):
        if width_val is None:
            return self._pulse_width
        self._pulse_width = int(width_val)
        self._i2c_write_word(self.hw.REG_PWM_CHN + self.channel, self._pulse_width)
        return self._pulse_width

    def pulse_width_percent(self, percentage=None):
        if percentage is None:
            return self._pulse_width_percent

        percentage = max(0.0, min(100.0, float(percentage)))
        self._pulse_width_percent = percentage

        calculated_width = (percentage / 100.0) * self._arr
        self.pulse_width(calculated_width)
        return self._pulse_width_percent

    def off(self) -> None:
        self.pulse_width_percent(0.0)
