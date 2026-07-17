"""
Data structure for calibration offsets and settings.
"""
from dataclasses import dataclass

@dataclass
class CalibrationData:
    """Stores base offsets for steering and throttle calculation."""
    neutral_lean_angle: float = 0.0
    neutral_wrist_rotation: float = 0.0
    is_calibrated: bool = False
