from reflex.bno08x.i2c import IMUDriver

features = {
    0x03: "MAGNETIC_FIELD",
    0x08: "GAME_ROTATION_VECTOR",
    0x10: "TAP_DETECTOR",
    0x12: "SIGNIFICANT_MOTION",
    0x13: "STABILITY_CLASSIFIER",
    0x19: "SHAKE_DETECTOR",
    0x1A: "FLIP_DETECTOR",
    0x1B: "PICKUP_DETECTOR",
    0x20: "TILT_DETECTOR",
}

def configure_imu(interval_us=10000):
    imu = IMUDriver(i2c_bus=1, address=0x4B)
    for fid, name in features.items():
        print("Enabling", name)
        imu.send_feature(fid, interval_us)
    print("IMU FEATURES ENABLED")
    return imu

if __name__ == "__main__":
    configure_imu()
