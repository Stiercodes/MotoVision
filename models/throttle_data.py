"""
Data structure for throttle information.
"""
from dataclasses import dataclass

@dataclass
class ThrottleData:
    """Stores wrist rotation angle and normalized throttle value."""
    raw_rotation: float = 0.0
    normalized_throttle: float = 0.0
