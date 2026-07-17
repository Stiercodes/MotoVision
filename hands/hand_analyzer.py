"""
Transforms raw MediaPipe hand coordinates into semantic hand measurements.
"""
import math
from typing import Tuple
from hands.hand_data import HandData
from hands.hand_metrics import HandMetrics

class HandAnalyzer:
    """Analyzes raw hand data to extract hand metrics."""
    def analyze(self, hand_data: HandData) -> HandMetrics:
        metrics = HandMetrics()
        
        if not hand_data.landmarks or len(hand_data.landmarks) < 21:
            return metrics
            
        lms = hand_data.landmarks
        
        # 1. Tracking Status and Quality
        metrics.tracking_quality = hand_data.confidence
        if metrics.tracking_quality > 0.7:
            metrics.tracking_status = "TRACKING"
        elif metrics.tracking_quality > 0.3:
            metrics.tracking_status = "LOW_CONFIDENCE"
        else:
            metrics.tracking_status = "NOT_TRACKED"

        if metrics.tracking_status == "NOT_TRACKED":
            return metrics

        # 2. Palm Orientation (Normal Vector, Pitch, Yaw)
        # Using Wrist (0), Index MCP (5), Pinky MCP (17)
        p0 = lms[0]
        p5 = lms[5]
        p17 = lms[17]
        
        # Vector 0->5
        v1 = [p5[0]-p0[0], p5[1]-p0[1], p5[2]-p0[2]]
        # Vector 0->17
        v2 = [p17[0]-p0[0], p17[1]-p0[1], p17[2]-p0[2]]
        
        # Cross product v1 x v2 gives normal vector
        nx = v1[1]*v2[2] - v1[2]*v2[1]
        ny = v1[2]*v2[0] - v1[0]*v2[2]
        nz = v1[0]*v2[1] - v1[1]*v2[0]
        
        mag = math.sqrt(nx**2 + ny**2 + nz**2)
        if mag > 0:
            nx /= mag
            ny /= mag
            nz /= mag
            
        metrics.palm_normal_vector = (nx, ny, nz)
        
        # Simple pitch/yaw from normal vector
        metrics.palm_pitch = math.degrees(math.atan2(ny, nz))
        metrics.palm_yaw = math.degrees(math.atan2(nx, nz))
        
        # 3. Wrist Roll Estimate
        # Using vector 17->5 relative to vertical
        dx = p5[0] - p17[0]
        dy = p5[1] - p17[1]
        metrics.wrist_roll_estimate = math.degrees(math.atan2(dy, dx))

        # 4. Grip Percentage and Hand Openness
        # Distance from fingertips (8, 12, 16, 20) to wrist (0)
        fingertips = [8, 12, 16, 20]
        total_dist = 0.0
        for tip in fingertips:
            pt = lms[tip]
            dist = math.sqrt((pt[0]-p0[0])**2 + (pt[1]-p0[1])**2)
            total_dist += dist
        avg_dist = total_dist / 4.0
        
        # Normalize (rough estimate, depends on hand size/distance)
        # Using distance between wrist and index MCP as a reference scale
        ref_scale = math.sqrt(v1[0]**2 + v1[1]**2)
        if ref_scale > 0.001:
            openness = avg_dist / ref_scale
            # Map openness roughly to 0-100%
            openness = max(0.0, min(1.0, (openness - 0.8) / 1.5))
            metrics.hand_openness = openness * 100.0
            metrics.grip_percentage = 100.0 - metrics.hand_openness

        # 5. Thumb Extension
        p4 = lms[4] # Thumb tip
        thumb_dist = math.sqrt((p4[0]-p5[0])**2 + (p4[1]-p5[1])**2)
        metrics.thumb_extension = thumb_dist / ref_scale if ref_scale > 0.001 else 0.0

        return metrics
