import pyaudio

p = pyaudio.PyAudio()
info = p.get_default_input_device_info()
print(info)