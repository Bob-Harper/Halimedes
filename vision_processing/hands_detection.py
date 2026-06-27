#!/usr/bin/env python3
from typing import Any, cast, List, Tuple
import cv2
import mediapipe.python.solutions.hands as mp_hands
import mediapipe.python.solutions.drawing_utils as mp_drawing

class DetectHands():
    def __init__(self):
        self.hands = mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def work(self, image):
        joints = []
        if image is not None and image.size != 0:
            image.flags.writeable = False
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # 1. Cast results to Any so Pylance stops complaining about NamedTuple
            results = cast(Any, self.hands.process(image_rgb))

            image.flags.writeable = True

            if results.multi_hand_landmarks:
                # 2. Cast HAND_CONNECTIONS to a list to satisfy the type checker
                connections = cast(List[Tuple[int, int]], mp_hands.HAND_CONNECTIONS)

                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        image,
                        hand_landmarks,
                        connections
                    )

                    # 3. Safely extract numerical values into a list of [x, y, z]
                    for landmark in hand_landmarks.landmark:
                        joints.append([
                            landmark.x,
                            landmark.y,
                            landmark.z
                        ])

        return image, joints
