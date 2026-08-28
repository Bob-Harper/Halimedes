# reflex/bno08x/enable_imu_reports.py
from crawler.bno08x.i2c import IMUDriver


features = {
    0x08: "GAME_ROTATION_VECTOR",
    }

def configure_imu(imu, interval_us=10000):
    for fid, name in features.items():
        print("[Startup] Enabling", name)
        imu.send_feature(fid, interval_us)
        imu.enabled_reports.append(fid)
    print("[Startup] IMU FEATURES ENABLED")
    return imu

if __name__ == "__main__":
    imu = IMUDriver(i2c_bus=1, address=0x4B)
    configure_imu(imu)
