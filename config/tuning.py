"""
Beginner-Friendly Tuning Configuration

This file contains all the user-adjustable settings for MotoVision.
You can freely modify these values to change how the steering and throttle feel.
"""

# ==========================================
# STEERING TUNING
# ==========================================

# Lower = Less body movement required (more sensitive)
# Higher = More body movement required (less sensitive)
STEERING_SENSITIVITY = 0.15

# Lower = Slower, smoother steering (more delay)
# Higher = Faster, sharper steering (less delay)
STEERING_SMOOTHING = 0.90

# The steering percentage required to press the steering key
# Lower = Key presses sooner (more sensitive)
# Higher = Key presses later (less sensitive)
STEERING_PRESS_THRESHOLD = 0.15

# How much the steering must drop from its peak to release the key
# Lower = Key releases very quickly when you start straightening
# Higher = Key waits longer before releasing
STEERING_RELEASE_DELTA = 0.05

# Output mode for steering keys.
# "hold" = Traditional behavior (keys are held continuously)
# "adaptive_pulse" = Keys are pulsed rapidly for small movements, held for large movements.
STEERING_OUTPUT_MODE = "adaptive_pulse"


# ==========================================
# THROTTLE TUNING
# ==========================================

# Lower = Slower, smoother throttle (more delay)
# Higher = Faster, sharper throttle (less delay)
THROTTLE_SMOOTHING = 0.15

# The throttle percentage required to press the Up Arrow
# Lower = Key presses sooner with less wrist twist
# Higher = Key presses later, requiring more wrist twist
THROTTLE_PRESS_THRESHOLD = 0.05

# How much the throttle must drop from its peak to release the key
# Lower = Key releases very quickly when you relax your wrist
# Higher = Key waits longer before releasing
THROTTLE_RELEASE_DELTA = 0.10
