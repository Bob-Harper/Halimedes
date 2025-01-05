import threading
from robot_hat import TTS
from picrawler import Picrawler

tts1 = TTS(engine='espeak')
tts1.espeak_params(amp=50, speed=220, gap=2, pitch=98)  # amp = volume, speed = 80 to 260, gap = time between words, pitch 0-98 deep or high voice
tts2 = TTS(engine='espeak')
tts2.espeak_params(amp=50, speed=180, gap=2, pitch=2)
crawler = Picrawler()


def sit_down():
    # Assuming these are the commands to lower the legs
    sit_down_steps = [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]]
    crawler.do_step(sit_down_steps, speed=60)

def twist(speed, stop_event):
    # stand_up()
    new_step = [[50, 50, -80], [50, 50, -80], [50, 50, -80], [50, 50, -80]]
    while not stop_event.is_set():
        for i in range(4):
            for inc in range(30, 60, 80):
                if stop_event.is_set():
                    break
                rise = [50, 50, (-80 + inc * 0.5)]
                drop = [50, 50, (-80 - inc)]
                new_step[i] = rise
                new_step[(i + 2) % 4] = drop
                new_step[(i + 1) % 4] = rise
                new_step[(i - 1) % 4] = drop
                crawler.do_step(new_step, speed)
    sit_down()

def wave_leg(stop_event):
    new_step = [[50, 50, -80], [50, 50, -80], [50, 50, -80], [50, 50, -80]]
    print(f"Waving leg {leg_index}...")
    speed = 100
    while not stop_event.is_set():
        for inc in range(0, 45, 5):
            if stop_event.is_set():
                break
            lift = [90, 120, 90 + inc]  # Adjust the vertical angles to wave
            lower = [90, 120, 90 - inc]
            new_step = [[90, 120, 90] for _ in range(4)]
            new_step[leg_index] = lift
            crawler.do_step(new_step, speed)
            sleep(0.1)
            new_step[leg_index] = lower
            crawler.do_step(new_step, speed)
            sleep(0.1)
    print(f"Waving leg {leg_index} completed.")

def speak_and_dance(tts, word1, word2, speed):
    stop_event = threading.Event()

    # Create a thread for speaking
    speak_thread = threading.Thread(target=tts1.say, args=(word1,))
    speak_thread2 = threading.Thread(target=tts2.say, args=(word2,))
    # Create a thread for dancing
    dance_thread = threading.Thread(target=twist, args=(speed, stop_event))

    # Start both threads
    speak_thread.start()
    dance_thread.start()

    # Wait for the speaking thread to finish
    speak_thread.join()
    speak_thread2.start()
    speak_thread2.join()
    # Signal the dancing thread to stop
    stop_event.set()
    # Wait for the dancing thread to finish
    dance_thread.join()

def main():
    word1 = "This is so exciting!    What are we going to do tonight, Bob?"
    word2 = "The same thing we do every night, Hal.  We try to take over the world!"
    # word = "Do you come from a land down under... Where women glow and men plunder?   Cant you hear, cant you hear the thunder?  You better run, you better take cover"
    # word = "Buying bread from a man in Brussels, He was six-foot-four and full of muscle. I said, Do you speak-a my language? He just smiled and gave me a Vegemite sandwich"
    # word = "Spank my booty, come on and spank my booty!  Spank my booty, spank it real good!"
    # word = "Moooooove bitch, get out the way, get out the way bitch, get out the way, Moooooove bitch, get out the way, get out the way bitch, get out the way"
    speak_and_dance(tts1, word1, word2, speed=90)
    # stand_up()

if __name__ == "__main__":
    main()
