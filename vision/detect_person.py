from vilib import Vilib
from time import sleep
from robot_hat import TTS
import cv2
import os

flag_face = False
tts = TTS()

# Path to the directory containing face images
faces_dir = os.path.join("memory", "faces")

# Example person to recognize (Bob)
known_people = {
    "Bob": os.path.join(faces_dir, "bob01.jpg")
}

MANUAL = '''
Input key to call the function!
    f: Switch ON/OFF face detect
'''

def recognize_person(face_image):
    # Load the known faces
    known_faces = {}
    for person, image_path in known_people.items():
        known_faces[person] = cv2.imread(image_path, cv2.IMREAD_COLOR)

    # Implement face recognition logic here
    # For simplicity, let's assume using OpenCV for face detection and template matching
    gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        # Extract the face region
        face_roi = gray[y:y+h, x:x+w]

        # Compare with known faces
        for person, known_face in known_faces.items():
            # Convert known face to grayscale for comparison
            known_face_gray = cv2.cvtColor(known_face, cv2.COLOR_BGR2GRAY)
            result = cv2.matchTemplate(face_roi, known_face_gray, cv2.TM_CCOEFF_NORMED)
            confidence = cv2.minMaxLoc(result)[1]

            # Adjust the confidence threshold as needed
            if confidence > 0.6:
                return person

    return None  # Return None if no match found

def face_detect(flag):
    global flag_face
    print("Face Detect: " + str(flag))
    # Ensure face detection is switched on/off correctly
    # Here, you would typically interact with Vilib for camera capture and detection,
    # but adapt according to how Vilib functions are used in your environment.

    if flag:
        Vilib.face_detect_switch(True)  # Assuming this starts face detection with Vilib

    while flag_face:
        if Vilib.detect_obj_parameter['human_n'] > 0:  # Check if human face detected
            print('Face Detected')
            face_image = Vilib.camera_capture()  # Capture frame using Vilib
            person = recognize_person(face_image)  # Recognize the person

            if person is not None:
                print(f"Recognized: {person}")
                tts.say(person)  # Speak the recognized person's name
            else:
                print("Unknown face detected.")
                tts.say("Who are you?")  # Ask the unknown person
            flag_face = False  # End the program after detecting a face
        else:
            sleep(2)  # Wait before checking again if no face detected

def main():
    global flag_face
    tts.lang("en-US")
    print(MANUAL)

    # Start your Vilib camera and any necessary initializations here
    # Vilib.camera_start(vflip=False, hflip=False)

    while True:
        # read key
        key = input("Enter command: ")
        key = key.lower()

        # face detection
        if key == "f":
            flag_face = not flag_face
            face_detect(flag_face)
        sleep(0.5)

    # Close the Vilib camera when done
    # Vilib.camera_close()
    # print("Camera closed.")

if __name__ == "__main__":
    main()
