from vilib import Vilib
from time import sleep
from robot_hat import TTS

flag_face = False
tts = TTS()

MANUAL = '''
Input key to call the function!
    f: Switch ON/OFF face detect
'''

def face_detect(flag):
    global flag_face
    print("Face Detect: " + str(flag))
    Vilib.face_detect_switch(flag)
    while flag:
        if 'human_n' in Vilib.detect_obj_parameter and Vilib.detect_obj_parameter['human_n'] > 0:
            print('Face Detected')
            spoken_text = "Face detected! Initiating response."
            tts.say(spoken_text)
            flag_face = False  # End the program after detecting a face
        else:

            sleep(2)

def main():
    global flag_face
    tts.lang("en-US")
    Vilib.camera_start(vflip=False, hflip=False)
    print(MANUAL)

    while True:
        # read key
        key = input("Enter command: ")
        key = key.lower()

        # face detection
        if key == "f":
            flag_face = not flag_face
            face_detect(flag_face)

if __name__ == "__main__":
    main()
