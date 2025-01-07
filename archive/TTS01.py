from robot_hat import TTS

# Initialize TTS with espeak engine
tts = TTS(engine="espeak")
tts.espeak_params(amp=180, speed=160, gap=1, pitch=50)

# Speak a test phrase
tts.say("Hello, Halimedes! I am speaking through the Robot HAT.")
