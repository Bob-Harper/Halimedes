#!/usr/bin/env python3
from typing import Any, cast, List, Tuple
import cv2
import mediapipe.python.solutions.pose as mp_pose
import mediapipe.python.solutions.drawing_utils as mp_drawing

class DetectPose():
    def __init__(self):
        self.pose = mp_pose.Pose(
            static_image_mode=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def work(self, image):
        joints = []
        if image is not None and image.size != 0:
            image.flags.writeable = False
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # 1. Cast results to Any so Pylance stops complaining about NamedTuple attributes
            results = cast(Any, self.pose.process(image_rgb))

            image.flags.writeable = True

            if results.pose_landmarks:
                # 2. Cast POSE_CONNECTIONS to a list to satisfy the type checker
                connections = cast(List[Tuple[int, int]], mp_pose.POSE_CONNECTIONS)

                mp_drawing.draw_landmarks(
                    image,
                    results.pose_landmarks,
                    connections
                )

                for landmark in results.pose_landmarks.landmark:
                    joints.append([
                        landmark.x,
                        landmark.y,
                        landmark.z,
                        landmark.visibility
                    ])

        return image, joints
