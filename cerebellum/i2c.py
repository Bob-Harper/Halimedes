# cerebellum/i2c.py
#!/usr/bin/env python3
from smbus2 import SMBus

class I2C:
    """
    Raw, high-performance native Python I2C hardware interface.
    Separates raw bus writes from memory register updates cleanly with zero bloat.
    """
    def __init__(self, address: int | list[int], bus: int = 1, *args, **kwargs):
        self._bus = bus
        self._smbus = SMBus(self._bus)
        self.address = None

        if isinstance(address, list):
            connected_devices = self.scan()
            for _addr in address:
                if _addr in connected_devices:
                    self.address = _addr
                    break
            else:
                self.address = address
        else:
            self.address = address

        if self.address is None:
            raise ValueError("I2C address cannot be None")

    def _write_byte(self, data):
        return self._smbus.write_byte(self.address, data)

    def _write_byte_data(self, reg, data):
        return self._smbus.write_byte_data(self.address, reg, data)

    def _write_word_data(self, reg, data):
        return self._smbus.write_word_data(self.address, reg, data)

    def _write_i2c_block_data(self, reg, data):
        return self._smbus.write_i2c_block_data(self.address, reg, data)

    def _read_byte(self):
        return self._smbus.read_byte(self.address)

    def _read_byte_data(self, reg):
        return self._smbus.read_byte_data(self.address, reg)

    def _read_word_data(self, reg):
        result = self._smbus.read_word_data(self.address, reg)
        return [result & 0xFF, (result >> 8) & 0xFF]

    def _read_i2c_block_data(self, reg, num):
        return self._smbus.read_i2c_block_data(self.address, reg, num)

    def is_ready(self):
        return self.address in self.scan()

    def scan(self):
        """Direct native hardware register bit poll sweep."""
        addresses = []
        for addr in range(0x03, 0x78):
            try:
                self._smbus.write_quick(addr)
                addresses.append(addr)
            except OSError:
                continue
        return addresses

    def write(self, data):
        """Send raw data directly down the bus (no register memory targeting)."""
        if isinstance(data, bytearray):
            data_all = list(data)
        elif isinstance(data, int):
            data_all = [0] if data == 0 else []
            while data > 0:
                data_all.append(data & 0xFF)
                data >>= 8
        elif isinstance(data, list):
            data_all = data
        else:
            raise ValueError(f"Write data must be int, list, or bytearray, not {type(data)}")

        if len(data_all) == 1:
            self._write_byte(data_all[0])
        else:
            # Send raw byte streaming block
            self._write_i2c_block_data(data_all[0], list(data_all[1:]))

    def mem_write(self, data, memaddr: int):
        """
        Send data targeted directly to a specific register memory address.
        Essential for setting PWM duty cycles, periods, and frequencies.
        """
        if isinstance(data, bytearray):
            data_all = list(data)
        elif isinstance(data, list):
            data_all = data
        elif isinstance(data, int):
            data_all = [0] if data == 0 else []
            while data > 0:
                data_all.append(data & 0xFF)
                data >>= 8
        else:
            raise ValueError("mem_write requires bytearray, list, or int data payload parameters.")

        # Target the register memory address with the clean data block array natively
        self._write_i2c_block_data(memaddr, data_all)

    def read(self, length=1):
        if not isinstance(length, int):
            raise ValueError(f"Length must be int, not {type(length)}")
        result = []
        for _ in range(length):
            result.append(self._read_byte())
        return result
