#!/usr/bin/env python3
from typing import Dict, Tuple, Any
import cv2
import numpy as np

# Static configuration mapping colors to their HSV threshold bounds
COLOR_DICT = {
    'red': [[0, 8], [80, 255], [0, 255]],
    'orange': [[12, 18], [80, 255], [80, 255]],
    'yellow': [[20, 60], [60, 255], [120, 255]],
    'green': [[45, 85], [120, 255], [80, 255]],
    'blue': [[92, 120], [120, 255], [80, 255]],
    'purple': [[115, 155], [30, 255], [60, 255]],
    'magenta': [[160, 180], [30, 255], [60, 255]],
}

class ColorDetector:
    def __init__(self) -> None:
        # State tracking isolated to the instance object to avoid cross-thread collision
        self.parameters: Dict[str, Any] = {
            'color': 'red',
            'x': 320,
            'y': 240,
            'w': 0,
            'h': 0,
            'n': 0
        }

    def color_detect_work(
        self,
        img: np.ndarray,
        width: int,
        height: int,
        color_name: str,
        rectangle_color: Tuple[int, int, int] = (0, 0, 255)
    ) -> np.ndarray:
        '''
        Color detection with OpenCV optimized for robot vision.
        '''
        self.parameters['color'] = color_name

        # Reduce image size for faster tracking performance
        zoom = 4
        width_zoom = int(width / zoom)
        height_zoom = int(height / zoom)
        resize_img = cv2.resize(img, (width_zoom, height_zoom), interpolation=cv2.INTER_LINEAR)

        # Convert BGR to HSV
        hsv = cv2.cvtColor(resize_img, cv2.COLOR_BGR2HSV)

        # FIX: Force strict 1D numpy array shapes to satisfy OpenCV's C++ signatures in Pylance
        color_lower = np.array([COLOR_DICT[color_name][0][0], COLOR_DICT[color_name][1][0], COLOR_DICT[color_name][2][0]], dtype=np.uint8)
        color_upper = np.array([COLOR_DICT[color_name][0][1], COLOR_DICT[color_name][1][1], COLOR_DICT[color_name][2][1]], dtype=np.uint8)

        mask = cv2.inRange(hsv, color_lower, color_upper)

        if color_name == 'red':
            # FIX: Wrapped values in numpy arrays explicitly to conform to signatures
            mask_2 = cv2.inRange(hsv, np.array([167, 0, 0], dtype=np.uint8), np.array([180, 255, 255], dtype=np.uint8))
            mask = cv2.bitwise_or(mask, mask_2)

        # 5x5 kernel for morphology operations
        kernel_5 = np.ones((5, 5), np.uint8)
        open_img = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel_5, iterations=1)

        # Find contours safely (compatible across OpenCV versions)
        contours_data = cv2.findContours(open_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = contours_data[0] if len(contours_data) == 2 else contours_data[1]

        self.parameters['n'] = len(contours)

        if self.parameters['n'] < 1:
            self.parameters['x'] = int(width / 2)
            self.parameters['y'] = int(height / 2)
            self.parameters['w'] = 0
            self.parameters['h'] = 0
            self.parameters['n'] = 0
        else:
            max_area = 0
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                if w >= 8 and h >= 8:
                    x *= zoom
                    y *= zoom
                    w *= zoom
                    h *= zoom

                    # Draw visual target markers
                    cv2.rectangle(img, (x, y), (x + w, y + h), rectangle_color, 2)
                    cv2.putText(
                        img, color_name, (x, y - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.72,
                        rectangle_color, 1, cv2.LINE_AA
                    )
                else:
                    continue

                # Save the metrics of the largest tracked color mass
                object_area = w * h
                if object_area > max_area:
                    max_area = object_area
                    self.parameters['x'] = int(x + w / 2)
                    self.parameters['y'] = int(y + h / 2)
                    self.parameters['w'] = w
                    self.parameters['h'] = h

        return img

# Test Runner
def test(color: str) -> None:
    print(f"Starting tracking pipeline for color: {color}")
    detector = ColorDetector()

    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        out_img = detector.color_detect_work(frame, 640, 480, color)

        # Access the parameters safely out of the instance
        # print(f"Target Center: ({detector.parameters['x']}, {detector.parameters['y']})")

        cv2.imshow('Color tracking active...', out_img)

        if cv2.waitKey(1) & 0xFF == ord('q') or cv2.waitKey(1) & 0xff == 27:
            break
        if cv2.getWindowProperty('Color tracking active...', 1) < 0:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    test('red')
