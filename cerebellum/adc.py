#!/usr/bin/env python3
from cerebellum.i2c import I2C

class ADC(I2C):
    """
    High-performance Analog-to-Digital Converter interface.
    All legacy parent class overhead, logging leaks, and redundant bus writes are purged.
    """
    ADDR = [0x14, 0x15]

    def __init__(self, chn, address=None, *args, **kwargs):
        """
        Initialize the ADC channel register map.
        :param chn: channel number (0-7 or string 'A0'-'A7')
        """
        target_addr = address if address is not None else self.ADDR
        super().__init__(target_addr, *args, **kwargs)

        # Parse string semantic channel names natively
        if isinstance(chn, str):
            if chn.startswith("A"):
                chn = int(chn[1:])
            else:
                raise ValueError(f'ADC channel should be between [A0, A7], not "{chn}"')

        if chn < 0 or chn > 7:
            raise ValueError(f'ADC channel should be between, not "{chn}"')

        # Map channel selection directly to the co-processor's internal register frame
        chn = 7 - chn
        self.chn = chn | 0x10

    def read(self):
        """
        Read the 12-bit raw analog conversion value from the hardware registers.

        :return: ADC resolution value (0-4095)
        :rtype: int
        """
        # Execute a native, atomic 16-bit word read across the bus channels
        # Your I2C._read_word_data returns a [low_byte, high_byte] list array matrix
        lsb, msb = self._read_word_data(self.chn)

        # Combine the bit planes into a clean 12-bit unsigned integer resolution scale
        return (msb << 8) + lsb

    def read_voltage(self) -> float:
        """
        Read the raw conversion value and scale it directly to the 3.3V reference plane.

        :return: Calculated voltage (0.0 to 3.3 Volts)
        :rtype: float
        """
        return (self.read() * 3.3) / 4095.0
