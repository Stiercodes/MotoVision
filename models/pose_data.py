"""
Data structure for pose landmarks.
"""
from dataclasses import dataclass, field
from typing import List, Tuple, Any

@dataclass
class PoseData:
    """Stores body landmark coordinates and visibility."""
    shoulders: Tuple[float, float] = (0.0, 0.0)
    wrists: Tuple[float, float] = (0.0, 0.0)
    
    # Milestone 1 additions
    # list of [x, y, z, visibility] for all 33 landmarks
    landmarks: List[List[float]] = field(default_factory=list) 
    # raw mediapipe results for drawing standard skeleton
    raw_results: Any = None 
