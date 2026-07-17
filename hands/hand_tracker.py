"""
Hand detection using MediaPipe Hands.
"""
import cv2
import time
import mediapipe as mp
from typing import List
from hands.hand_data import HandData

class HandTracker:
    """Wrapper for MediaPipe hands estimation."""
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            model_complexity=0 # Optimized for speed
        )

    def process_frame(self, rgb_frame) -> List[HandData]:
        """Process an RGB image frame and return hand landmarks."""
        hand_data_list = []
        
        results = self.hands.process(rgb_frame)
        
        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_landmarks, handedness_info in zip(results.multi_hand_landmarks, results.multi_handedness):
                h_data = HandData()
                h_data.raw_results = hand_landmarks
                h_data.handedness = handedness_info.classification[0].label # "Left" or "Right"
                h_data.confidence = handedness_info.classification[0].score
                h_data.timestamp = time.time()
                
                for lm in hand_landmarks.landmark:
                    h_data.landmarks.append([lm.x, lm.y, lm.z])
                
                hand_data_list.append(h_data)
                
        return hand_data_list
