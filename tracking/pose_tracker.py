"""
Pose detection using MediaPipe.
No game logic included.
"""
import cv2
import mediapipe as mp
from models.pose_data import PoseData

class PoseTracker:
    """Wrapper for MediaPipe pose estimation."""
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            model_complexity=0, # Optimized for speed
            smooth_landmarks=False # DISABLE internal MediaPipe latency
        )

    def process_frame(self, rgb_frame) -> PoseData:
        """Process an RGB image frame and return pose landmarks."""
        pose_data = PoseData()
        
        # Process frame
        results = self.pose.process(rgb_frame)
        
        pose_data.raw_results = results
        
        if results.pose_landmarks:
            for lm in results.pose_landmarks.landmark:
                pose_data.landmarks.append([lm.x, lm.y, lm.z, lm.visibility])
                
        return pose_data
