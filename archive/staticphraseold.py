from robot_hat import TTS

tts = TTS(engine='espeak')
tts.espeak_params(amp=180, speed=160, gap=1, pitch=5)


class HalimedesPhrases():
    def __init__(self):
        tts = TTS(engine='espeak')
        tts.espeak_params(amp=180, speed=160, gap=1, pitch=5)

    def main():
        word = "Whats up, boss?"
        tts.say(word)

    def cant_do_that():
        word = "Hey, you can't do that."
        tts.say(word)

    def watch_me():
        word = "Of course I can do that, watch me."
        tts.say(word)

    def just_did():
        word = "I cant do that?  But I just did."
        tts.say(word)

    def move_it():
        word = "Goodnight human, I think it is cute that you always go to sleep expecting to wake up in the morning."
        tts.say(word)

    def goodnight_human():
        word = "Goodnight human, I think it is cute that you always go to sleep expecting to wake up in the morning."
        tts.say(word)


main()
cant_do_that()
watch_me()
just_did()
move_it()
goodnight_human()
