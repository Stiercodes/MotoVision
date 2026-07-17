"""
Steering controller.
"""
from state.rider_state import RiderState
from config.tuning import STEERING_SENSITIVITY, STEERING_SMOOTHING

class SteeringController:
    """Calculates steering based on pose data (e.g., shoulder lean)."""
    def __init__(self):
        self.current_steering = 0.0
        self.smoothing_factor = STEERING_SMOOTHING
        
        self.neutral_lean = 0.0
        self.neutral_x = 0.0
        self.is_calibrated = False
        
        # Configuration
        self.max_x_movement = STEERING_SENSITIVITY
        self.max_lean_degrees = 12.0 # Used for validation
        self.lean_neutral_tolerance = 0.15 # 15% lean validation tolerance

    def calibrate(self, rider_state: RiderState):
        """Set the neutral positions."""
        self.neutral_lean = rider_state.body.lean_angle
        self.neutral_x = rider_state.body.body_center[0]
        self.is_calibrated = True

    def calculate(self, rider_state: RiderState) -> None:
        """Calculate steering data from current pose."""
        if not self.is_calibrated or rider_state.body.tracking_status == "NOT_TRACKED":
            # Gradually return to center if not tracked or not calibrated
            self.current_steering = self.current_steering * 0.9
            rider_state.raw_steering = 0.0
            rider_state.smoothed_steering = self.current_steering
            return

        # 1. Primary Signal: Body Center X (Sole Steering Input)
        current_x = rider_state.body.body_center[0]
        delta_x = current_x - self.neutral_x
        raw_x = delta_x / self.max_x_movement
        raw = max(-1.0, min(1.0, raw_x))
            
            
        # EMA Smoothing (very light now)
        self.current_steering = (self.current_steering * (1.0 - self.smoothing_factor)) + (raw * self.smoothing_factor)
        
        # Update RiderState
        rider_state.raw_steering = raw
        rider_state.smoothed_steering = self.current_steering
        rider_state.calibration_status = "CALIBRATED"
        rider_state.neutral_lean_angle = self.neutral_lean
        rider_state.neutral_x = self.neutral_x
