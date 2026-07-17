"""
Transforms raw MediaPipe coordinates into semantic human body measurements.
"""
import math
from typing import List
from models.pose_data import PoseData
from analysis.body_metrics import BodyMetrics

class BodyAnalyzer:
    """Analyzes raw pose data to extract body metrics."""
    def __init__(self):
        # Rolling history for stability calculation
        self.history_size = 5
        self.history = []

    def analyze(self, pose_data: PoseData) -> BodyMetrics:
        """Calculate body metrics from pose data."""
        metrics = BodyMetrics()
        
        if not pose_data.landmarks:
            metrics.tracking_status = "NOT_TRACKED"
            return metrics

        lms = pose_data.landmarks
        
        # Helper indices (MediaPipe mapping)
        NOSE = 0
        LEFT_SHOULDER = 11
        RIGHT_SHOULDER = 12
        LEFT_ELBOW = 13
        RIGHT_ELBOW = 14
        LEFT_WRIST = 15
        RIGHT_WRIST = 16
        LEFT_HIP = 23
        RIGHT_HIP = 24

        # Verify essential landmarks are visible enough
        essential_indices = [LEFT_SHOULDER, RIGHT_SHOULDER, LEFT_HIP, RIGHT_HIP]
        visibility_sum = sum([lms[idx][3] for idx in essential_indices])
        metrics.tracking_quality = visibility_sum / len(essential_indices)

        if metrics.tracking_quality > 0.7:
            metrics.tracking_status = "TRACKING"
        elif metrics.tracking_quality > 0.3:
            metrics.tracking_status = "LOW_CONFIDENCE"
        else:
            metrics.tracking_status = "NOT_TRACKED"

        if metrics.tracking_status == "NOT_TRACKED":
            return metrics

        # 1. Scale Factor (using shoulder width)
        ls, rs = lms[LEFT_SHOULDER], lms[RIGHT_SHOULDER]
        shoulder_width_2d = math.sqrt((ls[0] - rs[0])**2 + (ls[1] - rs[1])**2)
        metrics.scale_factor = shoulder_width_2d if shoulder_width_2d > 0.01 else 1.0

        # 2. Body Center
        lh, rh = lms[LEFT_HIP], lms[RIGHT_HIP]
        mid_shoulder = ((ls[0] + rs[0]) / 2, (ls[1] + rs[1]) / 2)
        mid_hip = ((lh[0] + rh[0]) / 2, (lh[1] + rh[1]) / 2)
        metrics.body_center = ((mid_shoulder[0] + mid_hip[0]) / 2, (mid_shoulder[1] + mid_hip[1]) / 2)

        # 3. Lean Angle
        dx = mid_shoulder[0] - mid_hip[0]
        dy = mid_shoulder[1] - mid_hip[1]
        # Angle from true vertical (straight up = 0 degrees)
        angle_rad = math.atan2(dx, -dy)
        metrics.lean_angle = math.degrees(angle_rad)

        # 4. Shoulder Angle
        s_dx = rs[0] - ls[0]
        s_dy = rs[1] - ls[1]
        s_angle_rad = math.atan2(s_dy, s_dx)
        metrics.shoulder_angle = math.degrees(s_angle_rad)

        # 5. Torso Rotation (Depth comparison)
        metrics.torso_rotation = (ls[2] - rs[2]) / metrics.scale_factor

        # 6. Head Offset
        nose = lms[NOSE]
        metrics.head_offset = (nose[0] - metrics.body_center[0], nose[1] - metrics.body_center[1])

        # 7. Elbow Angles (3D)
        metrics.left_elbow_angle = self._calculate_angle_3d(ls, lms[LEFT_ELBOW], lms[LEFT_WRIST])
        metrics.right_elbow_angle = self._calculate_angle_3d(rs, lms[RIGHT_ELBOW], lms[RIGHT_WRIST])

        # 8. Upper Body Stability
        upper_body_pts = [NOSE, LEFT_SHOULDER, RIGHT_SHOULDER, LEFT_ELBOW, RIGHT_ELBOW]
        current_pts = [lms[i][:2] for i in upper_body_pts]
        self.history.append(current_pts)
        if len(self.history) > self.history_size:
            self.history.pop(0)
            
        metrics.upper_body_stability = self._calculate_stability()

        return metrics

    def _calculate_angle_3d(self, p1: List[float], p2: List[float], p3: List[float]) -> float:
        """Calculate the inner angle between three 3D points at p2."""
        # Vector p2 -> p1
        v1 = [p1[0] - p2[0], p1[1] - p2[1], p1[2] - p2[2]]
        # Vector p2 -> p3
        v2 = [p3[0] - p2[0], p3[1] - p2[1], p3[2] - p2[2]]
        
        dot = v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2]
        mag1 = math.sqrt(v1[0]**2 + v1[1]**2 + v1[2]**2)
        mag2 = math.sqrt(v2[0]**2 + v2[1]**2 + v2[2]**2)
        
        if mag1 * mag2 == 0:
            return 180.0
            
        cos_theta = max(-1.0, min(1.0, dot / (mag1 * mag2)))
        return math.degrees(math.acos(cos_theta))

    def _calculate_stability(self) -> float:
        """Estimates stability based on recent movement history."""
        if len(self.history) < 2:
            return 1.0 # Perfectly stable if not enough data
            
        total_movement = 0.0
        for i in range(1, len(self.history)):
            prev = self.history[i-1]
            curr = self.history[i]
            for p_prev, p_curr in zip(prev, curr):
                dist = math.sqrt((p_curr[0] - p_prev[0])**2 + (p_curr[1] - p_prev[1])**2)
                total_movement += dist
                
        # Normalize stability: 0 (high movement) to 1.0 (no movement)
        avg_movement = total_movement / (len(self.history) - 1)
        # Assuming a movement of 0.05 is highly unstable
        stability = max(0.0, 1.0 - (avg_movement * 20)) 
        return stability
