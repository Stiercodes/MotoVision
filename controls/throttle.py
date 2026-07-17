"""
Throttle controller.
"""
from state.rider_state import RiderState
from config.tuning import THROTTLE_SMOOTHING

class ThrottleController:
    """Calculates and smooths throttle based on hand orientation."""
    def __init__(self):
        self.current_throttle = 0.0
        self.smoothing_factor = THROTTLE_SMOOTHING
        self.decay_rate = 0.02 # Rate at which throttle drops when hand is lost
        
        # Baseline calibration (assumed for MVP, will be calibrated later)
        # Assuming palm_pitch changes as wrist twists. 
        # These values will likely need tuning based on exact camera angle.
        self.neutral_pitch = -20.0
        self.max_throttle_pitch = 40.0

    def calculate(self, rider_state: RiderState) -> None:
        """Calculate throttle data from current RiderState."""
        raw = 0.0
        
        if rider_state.right_hand and rider_state.right_hand.tracking_status != "NOT_TRACKED":
            pitch = rider_state.right_hand.palm_pitch
            
            # Normalize to 0.0 - 1.0 based on assumed range
            if self.max_throttle_pitch > self.neutral_pitch:
                progress = (pitch - self.neutral_pitch) / (self.max_throttle_pitch - self.neutral_pitch)
            else:
                progress = (self.neutral_pitch - pitch) / (self.neutral_pitch - self.max_throttle_pitch)
                
            raw = max(0.0, min(1.0, progress))
            
            # EMA Smoothing
            self.current_throttle = (self.current_throttle * (1.0 - self.smoothing_factor)) + (raw * self.smoothing_factor)
        else:
            # Gradually decay if hand is lost
            self.current_throttle = max(0.0, self.current_throttle - self.decay_rate)
            
        # Update RiderState
        rider_state.raw_throttle = raw
        rider_state.smoothed_throttle = self.current_throttle
