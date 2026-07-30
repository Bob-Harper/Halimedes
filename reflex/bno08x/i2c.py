from struct import pack_into
import reflex.bno08x as bno08x
from adafruit_bus_device import i2c_device
from reflex.bno08x  import BNO08X, DATA_BUFFER_SIZE, Packet, PacketError
import board
import busio
from reflex.bno08x.imu_interpreter import IMUInterpreter
import time

_BNO08X_DEFAULT_ADDRESS = (0x4B)

class IMUDriver:
    def __init__(self, i2c_bus, address=0x4B):
        self.interpreter = IMUInterpreter()
        # Use the patched transport layer
        self.dev = BNO08X_I2C(i2c_bus, address=address, debug=False)
        self.enabled_reports = []


    def send_feature(self, feature_id, interval_us):
        payload = bytearray(16)

        payload[0] = 0xFD
        payload[1] = feature_id
        payload[2] = 0x00
        payload[3] = 0x00
        payload[4] = 0x00

        payload[5] = interval_us & 0xFF
        payload[6] = (interval_us >> 8) & 0xFF
        payload[7] = (interval_us >> 16) & 0xFF
        payload[8] = (interval_us >> 24) & 0xFF

        self.dev._send_packet(2, payload)

    def read_packet(self):
        try:
            return self.dev._read_packet()

        except PacketError:
            # normal: no packet available
            return None

        except Exception:
            # corruption: drop ONE BYTE and retry
            try:
                self.dev._read_byte()   # discard a single byte
            except:
                pass

            # try again immediately
            try:
                return self.dev._read_packet()
            except:
                return

    def read(self):
        try:
            pkt = self.read_packet()
        except PacketError:
            return None
        except OSError:
            return None
        except Exception:
            return None

        if not pkt:
            return None

        buf = pkt.data

        # malformed packets (too short)
        if len(buf) < 2:
            return None

        first = buf[0]

        # REAL reset packet: 01 02 ...
        if first == 0x01 and buf[1] == 0x02:
            # resend all enabled reports
            for rid in self.enabled_reports:
                self.send_feature(rid, 100000)
            return None

        # hub events (ignore)
        if first in (0xFC, 0xFD, 0xF8, 0xF0, 0x7C):
            return None

        # sensor packets
        if first == 0xFB:
            return self.interpreter.interpret(pkt)

        # unknown packets → ignore
        return None


    def read_raw(self):
        # This must call the low-level packet reader that does NOT interpret,
        # and does NOT discard non-0xFB packets.
        pkt = self.dev._read_packet()
        return pkt


class BNO08X_I2C(BNO08X):
    """Library for the BNO08x IMUs from Hillcrest Laboratories

    :param ~busio.I2C i2c_bus: The I2C bus the BNO08x is connected to.

    """

    def __init__(self, i2c_bus, reset=None, address=_BNO08X_DEFAULT_ADDRESS, debug=False):
        i2c = busio.I2C(board.SCL, board.SDA)
        self.bus_device_obj = i2c_device.I2CDevice(i2c, address)
        super().__init__(reset, debug)
        self.log_data = True # True to Log raw packets inside def _read_packet

    def _send_packet(self, channel, data):
        data_length = len(data)
        write_length = data_length + 4

        pack_into("<H", self._data_buffer, 0, write_length)
        self._data_buffer[2] = channel
        self._data_buffer[3] = self._sequence_number[channel]

        for idx, send_byte in enumerate(data):
            self._data_buffer[4 + idx] = send_byte

        packet = Packet(self._data_buffer)
        self._dbg("Sending packet:")
        self._dbg(packet)

        with self.bus_device_obj as i2c:
            i2c.write(self._data_buffer, end=write_length)

        # increment sequence number for this channel
        self._sequence_number[channel] = (self._sequence_number[channel] + 1) % 256

    # returns true if available data was read
    # the sensor will always tell us how much there is, so no need to track it ourselves

    def _read_header(self):
        """Reads the first 4 bytes available as a header"""
        with self.bus_device_obj as i2c:
            i2c.readinto(self._data_buffer, end=4)  # this is expecting a header
        packet_header = Packet.header_from_buffer(self._data_buffer)
        self._dbg(packet_header)
        return packet_header

    def _read_packet(self):
        # Read header
        with self.bus_device_obj as i2c:
            i2c.readinto(self._data_buffer, end=4)

        header = Packet.header_from_buffer(self._data_buffer)
        packet_byte_count = header.packet_byte_count

        if packet_byte_count == 0:
            # drop one byte and resync
            with self.bus_device_obj as i2c:
                i2c.readinto(self._data_buffer, end=1)
            return None

        # Read payload (packet_byte_count includes header)
        payload_length = packet_byte_count - 4
        if payload_length > 0:
            try:
                with self.bus_device_obj as i2c:
                    i2c.readinto(self._data_buffer, end=packet_byte_count)
            except OSError:
                # IMU dropped the payload mid-transfer → resync
                with self.bus_device_obj as i2c:
                    i2c.readinto(self._data_buffer, end=1)
                return None

        # Log raw packet
        if self.log_data:
            with open("data/raw_packet.log", "a") as f:
                ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + f".{int(time.time() * 1000) % 1000:03d}"
                f.write(f"Timestamp: {ts}\n")
                f.write(" ".join(f"{b:02X}" for b in self._data_buffer[:packet_byte_count]) + "\n\n")

        return Packet(self._data_buffer[:packet_byte_count])



    # returns true if all requested data was read
    def _read(self, requested_read_length):
        self._dbg("trying to read", requested_read_length, "bytes")
        # +4 for the header
        total_read_length = requested_read_length + 4
        if total_read_length > DATA_BUFFER_SIZE:
            self._data_buffer = bytearray(total_read_length)
            self._dbg(
                "!!!!!!!!!!!! ALLOCATION: increased _data_buffer to bytearray(%d) !!!!!!!!!!!!! "
                % total_read_length
            )
        with self.bus_device_obj as i2c:
            i2c.readinto(self._data_buffer, end=total_read_length)

    @property
    def _data_ready(self):
        header = self._read_header()

        if header.channel_number > 5:
            self._dbg("channel number out of range:", header.channel_number)
        if header.packet_byte_count == 0x7FFF:
            print("Byte count is 0x7FFF/0xFFFF; Error?")
            if header.sequence_number == 0xFF:
                print("Sequence number is 0xFF; Error?")
            ready = False
        else:
            ready = header.data_length > 0

        # self._dbg("\tdata ready", ready)
        return ready
