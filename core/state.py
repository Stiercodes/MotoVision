"""
Central application state management.
"""
from dataclasses import dataclass
from typing import Tuple

@dataclass
class AppState:
    """Stores the global state of the application."""
    fps: int = 0
    camera_connected: bool = False
    tracking_status: str = "Disconnected"
    pose_confidence: float = 0.0
    lean_angle: float = 0.0
    steering_value: float = 0.0
    throttle_value: float = 0.0
    calibration_status: str = "Not Calibrated"
    
    # Milestone 1 additions
    developer_mode: bool = False
    camera_resolution: Tuple[int, int] = (1280, 720)
    
    # Timing
    timings: dict = None
