import sounddevice as sd

def list_audio_devices():
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        print(f"Device {i}: {device['name']} (Input Channels: {device['max_input_channels']}, Output Channels: {device['max_output_channels']})")

if __name__ == "__main__":
    list_audio_devices()
    print(sd.query_devices(kind='input'))
