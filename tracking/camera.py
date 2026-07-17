"""
Webcam manager.
Responsible for opening, reading, and releasing the webcam.
"""
import cv2

class Camera:
    """Handles webcam stream and frame extraction."""
    def __init__(self, camera_index=0, width=1280, height=720, target_fps=60):
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.target_fps = target_fps
        self.cap = None

    def open(self) -> bool:
        """Opens the webcam and configures settings."""
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            return False
            
        # VERY IMPORTANT FOR LATENCY: Force camera to discard old frames
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.cap.set(cv2.CAP_PROP_FPS, self.target_fps)
        return True

    def read_frame(self):
        """Reads a frame from the webcam."""
        if not self.cap or not self.cap.isOpened():
            return False, None
            
        ret, frame = self.cap.read()
        if not ret:
            return False, None
            
        # Flip frame horizontally for a mirror effect (more natural)
        frame = cv2.flip(frame, 1)
        return True, frame

    def release(self):
        """Releases the webcam."""
        if self.cap:
            self.cap.release()
            self.cap = None

    def switch_camera(self) -> bool:
        """Cycles to the next available camera index."""
        self.release()
        self.camera_index += 1
        success = self.open()
        if not success:
            # Loop back to 0
            self.camera_index = 0
            success = self.open()
        return success
