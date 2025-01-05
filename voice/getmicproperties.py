import pyaudio

# Initialize PyAudio
p = pyaudio.PyAudio()

# Print device information
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    print(f"Device {i}: {info['name']} (Channels: {info['maxInputChannels']})")

p.terminate()
