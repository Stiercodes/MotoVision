"""
Data structure for steering information.
"""
from dataclasses import dataclass

@dataclass
class SteeringData:
    """Stores steering angle and normalized value."""
    raw_lean_angle: float = 0.0
    normalized_steering: float = 0.0
