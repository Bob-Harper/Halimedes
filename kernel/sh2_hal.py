import ctypes
import os
import time

_here = os.path.dirname(__file__)
lib = ctypes.CDLL(os.path.join(_here, "libsh2.so"))

# --- C function pointer types ---

OPEN_FN   = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p)
CLOSE_FN  = ctypes.CFUNCTYPE(None, ctypes.c_void_p)
READ_FN   = ctypes.CFUNCTYPE(ctypes.c_int,
                             ctypes.POINTER(ctypes.c_uint8),
                             ctypes.c_uint,
                             ctypes.c_void_p)
WRITE_FN  = ctypes.CFUNCTYPE(ctypes.c_int,
                             ctypes.POINTER(ctypes.c_uint8),
                             ctypes.c_uint,
                             ctypes.c_void_p)
TIME_FN   = ctypes.CFUNCTYPE(ctypes.c_uint32, ctypes.c_void_p)

# --- HAL struct (sh2_Hal_t) ---

class SH2Hal(ctypes.Structure):
    _fields_ = [
        ("open",    OPEN_FN),
        ("close",   CLOSE_FN),
        ("read",    READ_FN),
        ("write",   WRITE_FN),
        ("getTimeUs", TIME_FN),
        ("cookie",  ctypes.c_void_p),
    ]

# --- Bind sh2_open / sh2_close ---

lib.sh2_open.argtypes = [ctypes.POINTER(SH2Hal), ctypes.c_void_p, ctypes.c_void_p]
lib.sh2_open.restype  = ctypes.c_int

lib.sh2_close.argtypes = []
lib.sh2_close.restype  = None


class Sh2Host:
    """
    Python-side HAL + SH-2 host wrapper.
    For now: minimal dummy HAL that opens cleanly.
    """

    def __init__(self):
        # store callbacks so they don't get GC'd
        self._open_cb  = OPEN_FN(self._open)
        self._close_cb = CLOSE_FN(self._close)
        self._read_cb  = READ_FN(self._read)
        self._write_cb = WRITE_FN(self._write)
        self._time_cb  = TIME_FN(self._time)

        # cookie can later hold a Python object (e.g. I2C bus handle)
        self._cookie = None

        self._hal = SH2Hal(
            self._open_cb,
            self._close_cb,
            self._read_cb,
            self._write_cb,
            self._time_cb,
            None  # cookie
        )

        self._is_open = False

    # ---- C callback implementations ----

    def _open(self, cookie):
        # TODO: real I2C init here
        return 0

    def _close(self, cookie):
        # TODO: real I2C teardown here
        pass

    def _read(self, buf, length, cookie):
        # TODO: real I2C read into buf[0:length]
        # return number of bytes read, or <0 on error
        return 0

    def _write(self, buf, length, cookie):
        # TODO: real I2C write from buf[0:length]
        # return number of bytes written, or <0 on error
        return length

    def _time(self, cookie):
        # microseconds since some epoch
        return int(time.time() * 1_000_000)

    # ---- Public API ----

    def open(self):
        if self._is_open:
            return 0
        rc = lib.sh2_open(ctypes.byref(self._hal), None, None)
        if rc == 0:
            self._is_open = True
        return rc

    def close(self):
        if not self._is_open:
            return
        lib.sh2_close()
        self._is_open = False

    def poll(self):
        return {
            "quat": (0.0, 0.0, 0.0, 1.0),
            "accel": (0.0, 0.0, 0.0),
            "gyro": (0.0, 0.0, 0.0),

            # orientation
            "pitch_deg": 0.0,
            "roll_deg": 0.0,
            "yaw_deg": 0.0,      # will eventually be mag+gyro fused heading
            "tilt_deg": 0.0,

            # magnetometer
            "mag": (0.0, 0.0, 0.0),   # raw µT-ish XYZ
            "heading_deg": 0.0,       # compass-like, 0–360
            "mag_strength": 0.0,      # |mag|, for interference checks

            "timestamp_us": self._time(None),
        }





if __name__ == "__main__":
    sh = Sh2Host()
    rc = sh.open()
    print("sh2_open() ->", rc)
    sh.close()
