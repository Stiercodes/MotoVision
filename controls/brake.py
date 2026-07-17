"""
Brake controller.
"""
from state.rider_state import RiderState

class BrakeController:
    """Calculates brake state based on left hand grip."""
    def __init__(self):
        # Configuration
        self.grip_threshold = 70.0 # If grip percentage > 70%, brake is applied
        
    def calculate(self, rider_state: RiderState) -> None:
        """Calculate brake data from current RiderState."""
        if not rider_state.left_hand or rider_state.left_hand.tracking_status == "NOT_TRACKED":
            rider_state.brake_applied = False
            rider_state.raw_brake = 0.0
            return
            
        grip = rider_state.left_hand.grip_percentage
        rider_state.raw_brake = grip
        
        if grip > self.grip_threshold:
            rider_state.brake_applied = True
        else:
            rider_state.brake_applied = False
