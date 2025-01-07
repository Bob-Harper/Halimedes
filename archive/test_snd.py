import os
try:
    os.open("/dev/snd/controlC3", os.O_RDWR)
    print("Access successful")
except PermissionError as e:
    print(f"Permission error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
