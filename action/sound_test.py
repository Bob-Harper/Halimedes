
'''
    Sorry, currently there is only sound when running with sudo
'''

from time import sleep
from robot_hat import Music,TTS

music = Music()
tts = TTS()

manual = '''
Input key to call the function!

    1: Play test 1
    1: Play test 2
    1: Play test 3

    Ctrl^C: quit
'''

def main():
    print(manual)

    flag_bgm = False
    music.music_set_volume(100)
    tts.lang("en-US")


    while True:
        key = input()
        key = key.lower()
        if key == "1":
            music.sound_play('./sounds/test.wav')
            sleep(0.05)
        elif key == "2":
            music.sound_play('./sounds/test2.wav')
            sleep(0.05)

        elif key == "3":
            music.sound_play('./sounds/test3.wav')
            sleep(0.05)


if __name__ == "__main__":
    main()

