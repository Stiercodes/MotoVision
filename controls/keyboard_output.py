"""
Keyboard output controller for macOS.
"""
from pynput.keyboard import Key, Controller
from state.rider_state import RiderState
from config.tuning import (
    STEERING_PRESS_THRESHOLD,
    STEERING_RELEASE_DELTA,
    THROTTLE_PRESS_THRESHOLD,
    THROTTLE_RELEASE_DELTA
)

class KeyboardController:
    """Translates RiderState into physical keyboard outputs."""
    def __init__(self):
        self.keyboard = Controller()
        
        # Configuration Thresholds
        self.throttle_trigger = THROTTLE_PRESS_THRESHOLD
        
        # Internal State
        self.up_pressed = False
        self.down_pressed = False
        self.left_pressed = False
        self.right_pressed = False
        
        self.logical_left_active = False
        self.logical_right_active = False
        self.pulse_phase = "RELEASED"
        self.pulse_timer_start = 0.0
        
        self.peak_left_steer = 0.0
        self.peak_right_steer = 0.0
        
        self.valley_left_steer = 0.0
        self.valley_right_steer = 0.0
        
        self.peak_throttle = 0.0
        self.valley_throttle = 0.0

    def calculate(self, rider_state: RiderState) -> None:
        """Evaluate rider state and press/release keys accordingly."""
        # Safety Check: If body tracking is completely lost, release everything
        if rider_state.body.tracking_status == "NOT_TRACKED":
            self.release_all()
            return
            
        # 1. Throttle (Up Arrow) with Dynamic Peak & Valley Tracking
        throttle = rider_state.smoothed_throttle
        throttle_dynamic_drop = THROTTLE_RELEASE_DELTA
        
        # Reset states when in neutral deadzone
        if throttle <= self.throttle_trigger:
            self.peak_throttle = 0.0
            self.valley_throttle = 0.0
            
        if throttle > self.throttle_trigger:
            if not self.up_pressed:
                if self.valley_throttle == 0.0:
                    # Fresh entry from neutral
                    self._press_key(Key.up)
                    self.peak_throttle = throttle
                else:
                    # Track the valley
                    self.valley_throttle = min(self.valley_throttle, throttle)
                    # Re-engage if they push past the valley
                    if throttle > self.valley_throttle:
                        self._press_key(Key.up)
                        self.peak_throttle = throttle
                        self.valley_throttle = 0.0
            else:
                # Actively accelerating. Track peak
                if self.peak_throttle == 0.0:
                    self.peak_throttle = throttle
                else:
                    self.peak_throttle = max(self.peak_throttle, throttle)
                    
                # Dynamic release check
                if throttle <= self.peak_throttle - throttle_dynamic_drop:
                    self._release_key(Key.up)
                    self.valley_throttle = throttle
        else:
            self._release_key(Key.up)
            self.peak_throttle = 0.0
            self.valley_throttle = 0.0

        # Brake (Down Arrow)
        if rider_state.brake_applied:
            self._press_key(Key.down)
        else:
            self._release_key(Key.down)
            
        # 2. Steering (Left / Right Arrows) with Dynamic Peak & Valley Tracking
        steer = rider_state.smoothed_steering
        
        trigger_press = STEERING_PRESS_THRESHOLD
        dynamic_drop = STEERING_RELEASE_DELTA
        
        # Reset states when in neutral deadzone
        if -0.10 <= steer <= 0.10:
            self.peak_left_steer = 0.0
            self.peak_right_steer = 0.0
            self.valley_left_steer = 0.0
            self.valley_right_steer = 0.0
        
        # Steer Left (Negative)
        if steer < -trigger_press:
            if not self.logical_left_active:
                if self.valley_left_steer == 0.0:
                    self.logical_left_active = True
                    self.logical_right_active = False
                    self.peak_left_steer = steer
                else:
                    self.valley_left_steer = max(self.valley_left_steer, steer)
                    if steer < self.valley_left_steer:
                        self.logical_left_active = True
                        self.logical_right_active = False
                        self.peak_left_steer = steer
                        self.valley_left_steer = 0.0
            else:
                if self.peak_left_steer == 0.0:
                    self.peak_left_steer = steer
                else:
                    self.peak_left_steer = min(self.peak_left_steer, steer)
                if steer >= self.peak_left_steer + dynamic_drop:
                    self.logical_left_active = False
                    self.valley_left_steer = steer
        else:
            self.logical_left_active = False
            self.peak_left_steer = 0.0
            self.valley_left_steer = 0.0

        # Steer Right (Positive)
        if steer > trigger_press:
            if not self.logical_right_active:
                if self.valley_right_steer == 0.0:
                    self.logical_right_active = True
                    self.logical_left_active = False
                    self.peak_right_steer = steer
                else:
                    self.valley_right_steer = min(self.valley_right_steer, steer)
                    if steer > self.valley_right_steer:
                        self.logical_right_active = True
                        self.logical_left_active = False
                        self.peak_right_steer = steer
                        self.valley_right_steer = 0.0
            else:
                if self.peak_right_steer == 0.0:
                    self.peak_right_steer = steer
                else:
                    self.peak_right_steer = max(self.peak_right_steer, steer)
                if steer <= self.peak_right_steer - dynamic_drop:
                    self.logical_right_active = False
                    self.valley_right_steer = steer
        else:
            self.logical_right_active = False
            self.peak_right_steer = 0.0
            self.valley_right_steer = 0.0
            
        # Apply output mode
        from config.tuning import STEERING_OUTPUT_MODE
        if STEERING_OUTPUT_MODE == "adaptive_pulse":
            self._apply_adaptive_pulse(rider_state.timestamp, steer)
        else:
            if self.logical_left_active:
                self._release_key(Key.right)
                self._press_key(Key.left)
            elif self.logical_right_active:
                self._release_key(Key.left)
                self._press_key(Key.right)
            else:
                self._release_key(Key.left)
                self._release_key(Key.right)

    def _apply_adaptive_pulse(self, timestamp, steer):
        active_key = None
        if self.logical_left_active:
            active_key = Key.left
            self._release_key(Key.right)
        elif self.logical_right_active:
            active_key = Key.right
            self._release_key(Key.left)
        else:
            self._release_key(Key.left)
            self._release_key(Key.right)
            self.pulse_phase = "RELEASED"
            return
            
        abs_steer = abs(steer)
        
        if abs_steer > 0.65:
            self._press_key(active_key)
            self.pulse_phase = "PRESSED"
            self.pulse_timer_start = timestamp
            return
            
        if abs_steer > 0.35:
            press_duration = 0.125
            release_duration = 0.040
        else:
            press_duration = 0.050
            release_duration = 0.050
            
        elapsed = timestamp - self.pulse_timer_start
        
        if self.pulse_phase == "PRESSED":
            if elapsed >= press_duration:
                self._release_key(active_key)
                self.pulse_phase = "RELEASED"
                self.pulse_timer_start = timestamp
            else:
                self._press_key(active_key)
        else:
            if elapsed >= release_duration:
                self._press_key(active_key)
                self.pulse_phase = "PRESSED"
                self.pulse_timer_start = timestamp
            else:
                self._release_key(active_key)

    def release_all(self):
        """Emergency release all tracked keys."""
        self._release_key(Key.up)
        self._release_key(Key.down)
        self._release_key(Key.left)
        self._release_key(Key.right)

    def _press_key(self, key_obj):
        if key_obj == Key.up and not self.up_pressed:
            self.keyboard.press(Key.up)
            self.up_pressed = True
        elif key_obj == Key.down and not self.down_pressed:
            self.keyboard.press(Key.down)
            self.down_pressed = True
        elif key_obj == Key.left and not self.left_pressed:
            self.keyboard.press(Key.left)
            self.left_pressed = True
        elif key_obj == Key.right and not self.right_pressed:
            self.keyboard.press(Key.right)
            self.right_pressed = True

    def _release_key(self, key_obj):
        if key_obj == Key.up and self.up_pressed:
            self.keyboard.release(Key.up)
            self.up_pressed = False
        elif key_obj == Key.down and self.down_pressed:
            self.keyboard.release(Key.down)
            self.down_pressed = False
        elif key_obj == Key.left and self.left_pressed:
            self.keyboard.release(Key.left)
            self.left_pressed = False
        elif key_obj == Key.right and self.right_pressed:
            self.keyboard.release(Key.right)
            self.right_pressed = False
