"""
Data structure for generic hand measurements.
"""
from dataclasses import dataclass
from typing import Tuple

@dataclass
class HandMetrics:
    """Stores generic hand measurements."""
    tracking_status: str = "NOT_TRACKED"
    tracking_quality: float = 0.0
    palm_normal_vector: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    palm_pitch: float = 0.0
    palm_yaw: float = 0.0
    wrist_roll_estimate: float = 0.0
    grip_percentage: float = 0.0
    thumb_extension: float = 0.0
    hand_openness: float = 0.0
