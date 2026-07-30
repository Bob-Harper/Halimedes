import board
import busio
from reflex.bno08x.i2c import IMUDriver

i2c = busio.I2C(board.SCL, board.SDA)
imu = IMUDriver(i2c, address=0x4B)

# SHTP Command: GET ERROR (0xF2)
GET_ERROR = 0xF2

def get_error_buffer(imu):
    # SH-2 Command: GET ERROR (0xF2)
    payload = bytearray([0xF2])

    # Send on Control channel (channel 2)
    imu.dev._send_packet(2, payload)

    # Read the response packet
    pkt = imu.dev._read_packet()
    return pkt

print("Requesting IMU error buffer...")
err = get_error_buffer(imu)
print("Error buffer packet:", err)
