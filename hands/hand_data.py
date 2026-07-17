"""
Data structure for raw hand landmarks.
"""
from dataclasses import dataclass, field
from typing import List, Any

@dataclass
class HandData:
    """Stores raw hand landmarks from MediaPipe."""
    landmarks: List[List[float]] = field(default_factory=list)
    handedness: str = "Unknown"  # "Left" or "Right"
    confidence: float = 0.0
    visibility: float = 0.0
    timestamp: float = 0.0
    raw_results: Any = None
