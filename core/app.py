"""
Main Application Controller
Responsible for initializing modules and running the main update loop.
"""
import cv2
import time
from core.state import AppState
from tracking.camera import Camera
from tracking.pose_tracker import PoseTracker
from ui.overlay import Overlay
from analysis.body_analyzer import BodyAnalyzer
from hands.hand_tracker import HandTracker
from hands.hand_analyzer import HandAnalyzer
from state.rider_state import RiderState
from controls.throttle import ThrottleController
from controls.steering import SteeringController
from controls.keyboard_output import KeyboardController
from controls.brake import BrakeController

class App:
    """Main Application Controller."""
    def __init__(self):
        """Initialize the application components."""
        self.state = AppState()
        
        print("Initializing Camera...")
        self.camera = Camera(camera_index=0, width=1280, height=720, target_fps=60)
        
        print("Initializing Pose Tracker...")
        self.pose_tracker = PoseTracker()
        
        print("Initializing Hand Tracker...")
        self.hand_tracker = HandTracker()
        
        print("Initializing Body Analyzer...")
        self.body_analyzer = BodyAnalyzer()
        
        print("Initializing Hand Analyzer...")
        self.hand_analyzer = HandAnalyzer()
        
        print("Initializing Throttle Controller...")
        self.throttle_controller = ThrottleController()
        print("Initializing Brake Controller...")
        self.brake_controller = BrakeController()
        print("Initializing Steering Controller...")
        self.steering_controller = SteeringController()
        
        print("Initializing Keyboard Controller...")
        self.keyboard_controller = KeyboardController()
        
        print("Initializing UI Overlay...")
        self.overlay = Overlay()
        
        self.prev_frame_time = 0
        self.frame_id = 0

    def run(self):
        """Main update loop."""
        if not self.camera.open():
            print("Failed to open camera.")
            self.state.camera_connected = False
            return
            
        self.state.camera_connected = True
        self.state.camera_resolution = (self.camera.width, self.camera.height)
        
        print("MotoVision Engine Started. Press 'Q' to quit, 'D' for Developer Mode, 'C' to Calibrate, 'V' to switch Camera.")
        
        try:
            while True:
                ret, frame = self.camera.read_frame()
                if not ret:
                    print("Camera disconnected.")
                    self.state.camera_connected = False
                    break
                    
                self.frame_id += 1
                curr_time = time.time()
                t0 = time.perf_counter() # CAMERA DONE
                fps = 1 / (curr_time - self.prev_frame_time) if self.prev_frame_time > 0 else 0
                self.prev_frame_time = curr_time
                self.state.fps = int(fps)

                # 1. Tracking
                # Perform a single conversion and set writeable=False to bypass internal MediaPipe copies
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                rgb_frame.flags.writeable = False
                
                pose_data = self.pose_tracker.process_frame(rgb_frame)
                t1 = time.perf_counter() # POSE DONE
                
                hands_data_list = self.hand_tracker.process_frame(rgb_frame)
                rgb_frame.flags.writeable = True
                
                # 2. Analysis
                body_metrics = self.body_analyzer.analyze(pose_data)
                t2 = time.perf_counter() # BODY ANALYSIS DONE
                
                right_hand_metrics = None
                left_hand_metrics = None
                for hand_data in hands_data_list:
                    metrics = self.hand_analyzer.analyze(hand_data)
                    if hand_data.handedness == "Right":
                        right_hand_metrics = metrics
                    else:
                        left_hand_metrics = metrics
                
                # 3. Assemble Rider State
                overall_quality = body_metrics.tracking_quality
                overall_status = body_metrics.tracking_status
                if right_hand_metrics and right_hand_metrics.tracking_status != "NOT_TRACKED":
                    overall_status = "TRACKING"
                if left_hand_metrics and left_hand_metrics.tracking_status != "NOT_TRACKED":
                    overall_status = "TRACKING"

                rider_state = RiderState(
                    body=body_metrics,
                    right_hand=right_hand_metrics,
                    left_hand=left_hand_metrics,
                    frame_id=self.frame_id,
                    timestamp=curr_time,
                    tracking_quality=overall_quality,
                    tracking_status=overall_status
                )
                
                # Update global state (for basic UI)
                self.state.tracking_status = rider_state.tracking_status
                self.state.pose_confidence = rider_state.tracking_quality

                # 4. Calculate Controls
                self.throttle_controller.calculate(rider_state)
                self.brake_controller.calculate(rider_state)
                
                t3 = time.perf_counter() # PRE-STEERING
                self.steering_controller.calculate(rider_state)
                t4 = time.perf_counter() # STEERING DONE
                
                self.keyboard_controller.calculate(rider_state)
                t5 = time.perf_counter() # KEYBOARD DONE
                
                self.state.timings = {
                    "Camera -> Pose": (t1 - t0) * 1000,
                    "Pose -> Body Analysis": (t2 - t1) * 1000,
                    "Body Analysis -> Steering Calc": (t4 - t3) * 1000,
                    "Steering -> Keyboard Output": (t5 - t4) * 1000
                }

                # 5. Draw UI
                self.overlay.draw(frame, self.state, pose_data, hands_data_list, rider_state, self.keyboard_controller)

                # 6. Display
                cv2.imshow("MotoVision", frame)

                key = cv2.waitKey(1) & 0xFF
                if key in (ord('q'), ord('Q')):
                    break
                elif key in (ord('d'), ord('D')):
                    self.state.developer_mode = not self.state.developer_mode
                elif key in (ord('c'), ord('C')):
                    if rider_state.body.tracking_status != "NOT_TRACKED":
                        self.steering_controller.calibrate(rider_state)
                        print(f"Calibrated Neutral X: {rider_state.body.body_center[0]:.3f}, Lean: {rider_state.body.lean_angle:.2f}")
                elif key in (ord('v'), ord('V')):
                    print("Switching camera source...")
                    self.camera.switch_camera()
                    if not self.camera.cap or not self.camera.cap.isOpened():
                        print("Failed to find a working camera.")
                        self.state.camera_connected = False
                        break

        finally:
            print("Shutting down...")
            self.keyboard_controller.release_all()
            self.camera.release()
            cv2.destroyAllWindows()
