"""
Data structure for human body measurements.
"""
from dataclasses import dataclass
from typing import Tuple

@dataclass
class BodyMetrics:
    """Stores human body measurements derived from pose data."""
    tracking_status: str = "NOT_TRACKED"
    tracking_quality: float = 0.0
    lean_angle: float = 0.0
    shoulder_angle: float = 0.0
    torso_rotation: float = 0.0
    body_center: Tuple[float, float] = (0.0, 0.0)
    head_offset: Tuple[float, float] = (0.0, 0.0)
    left_elbow_angle: float = 180.0
    right_elbow_angle: float = 180.0
    scale_factor: float = 1.0
    upper_body_stability: float = 1.0
