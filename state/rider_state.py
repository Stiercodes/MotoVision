"""
Unified Rider State representing the complete user.
"""
from dataclasses import dataclass
from typing import Optional
from analysis.body_metrics import BodyMetrics
from hands.hand_metrics import HandMetrics

@dataclass
class RiderState:
    """Central representation of the user."""
    body: BodyMetrics
    right_hand: Optional[HandMetrics] = None
    left_hand: Optional[HandMetrics] = None
    frame_id: int = 0
    timestamp: float = 0.0
    tracking_quality: float = 0.0
    tracking_status: str = "NOT_TRACKED"
    
    # Milestone 4 additions
    raw_throttle: float = 0.0
    smoothed_throttle: float = 0.0
    
    # Milestone 7 additions
    raw_brake: float = 0.0
    brake_applied: bool = False
    
    # Milestone 5 additions
    raw_steering: float = 0.0
    smoothed_steering: float = 0.0
    calibration_status: str = "NOT CALIBRATED"
    neutral_lean_angle: float = 0.0
    neutral_x: float = 0.0
