from vilib import Vilib
import asyncio


class VisionHelper:
    def __init__(self):
        """Initialize the VisionHelper with default states."""
        self.face_detected = False

    def start_camera(self):
        """Start the camera and initialize settings."""
        Vilib.camera_start(vflip=False, hflip=False)
        Vilib.display(local=False, web=False)

    def stop_camera(self):
        """Stop the camera."""
        Vilib.camera_close()

    def enable_face_detection(self):
        """Enable face detection."""
        Vilib.face_detect_switch(True)

    def disable_face_detection(self):
        """Disable face detection."""
        Vilib.face_detect_switch(False)

    def is_face_detected(self):
        """Check if a face is detected."""
        if 'human_n' in Vilib.detect_obj_parameter and Vilib.detect_obj_parameter['human_n'] > 0:
            return True
        return False

    async def search_for_face(self, search_steps=4, delay=1):
        """
        Search for a face by moving and scanning.
        
        :param search_steps: Number of movements to perform during search.
        :param delay: Time to wait between movements (in seconds).
        :return: True if a face is found, False otherwise.
        """
        print("Searching for a face...")
        for _ in range(search_steps):
            if self.is_face_detected():
                print("Face found!")
                return True
            print("No face detected, adjusting position...")
            # Here, you can implement precise movements like turning
            await asyncio.sleep(delay)
        print("Search complete: No face detected.")
        return False
