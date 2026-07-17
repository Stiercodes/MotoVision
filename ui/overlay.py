"""
Debugging overlay.
"""
import cv2
import mediapipe as mp
from typing import List
from core.state import AppState
from models.pose_data import PoseData
from hands.hand_data import HandData
from state.rider_state import RiderState
from controls.keyboard_output import KeyboardController

class Overlay:
    """Draws debugging information over the webcam feed."""
    def __init__(self):
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose
        self.mp_hands = mp.solutions.hands
        self.font = cv2.FONT_HERSHEY_SIMPLEX

    def draw(self, frame, state_data: AppState, pose_data: PoseData, hands_data_list: List[HandData], rider_state: RiderState, keyboard_controller: KeyboardController = None):
        """Render the overlay on the current frame."""
        h, w, _ = frame.shape
        
        # 1. Draw MediaPipe Skeleton (Body)
        if pose_data.raw_results and pose_data.raw_results.pose_landmarks:
            self.mp_drawing.draw_landmarks(
                frame, 
                pose_data.raw_results.pose_landmarks, 
                self.mp_pose.POSE_CONNECTIONS,
                self.mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2),
                self.mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2)
            )
            
            # Custom Body Lines
            if len(pose_data.landmarks) > 0:
                lms = pose_data.landmarks
                
                def get_pt(idx):
                    if idx < len(lms) and lms[idx][3] > 0.5:
                        return (int(lms[idx][0] * w), int(lms[idx][1] * h))
                    return None
                    
                ls = get_pt(self.mp_pose.PoseLandmark.LEFT_SHOULDER.value)
                rs = get_pt(self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value)
                lh = get_pt(self.mp_pose.PoseLandmark.LEFT_HIP.value)
                rh = get_pt(self.mp_pose.PoseLandmark.RIGHT_HIP.value)
                
                if ls and rs:
                    cv2.line(frame, ls, rs, (255, 255, 0), 3)
                if lh and rh:
                    cv2.line(frame, lh, rh, (255, 255, 0), 3)
                if ls and rs and lh and rh:
                    mid_shoulder = ((ls[0] + rs[0]) // 2, (ls[1] + rs[1]) // 2)
                    mid_hip = ((lh[0] + rh[0]) // 2, (lh[1] + rh[1]) // 2)
                    cv2.line(frame, mid_shoulder, mid_hip, (0, 255, 255), 3)
                    
                    body_center = ((mid_shoulder[0] + mid_hip[0]) // 2, (mid_shoulder[1] + mid_hip[1]) // 2)
                    cv2.circle(frame, body_center, 8, (0, 0, 255), -1)

        # 2. Draw MediaPipe Hands
        for hand_data in hands_data_list:
            if hand_data.raw_results:
                self.mp_drawing.draw_landmarks(
                    frame,
                    hand_data.raw_results,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing.DrawingSpec(color=(121,22,76), thickness=2, circle_radius=2),
                    self.mp_drawing.DrawingSpec(color=(250,44,250), thickness=2, circle_radius=2)
                )

        # 3. Developer Mode Visuals (IDs and dots)
        if state_data.developer_mode:
            if pose_data.landmarks:
                for idx, lm in enumerate(pose_data.landmarks):
                    if lm[3] > 0.2:
                        px, py = int(lm[0] * w), int(lm[1] * h)
                        cv2.circle(frame, (px, py), 4, (0, 255, 0), -1)
                        text = f"ID:{idx} ({lm[0]:.2f},{lm[1]:.2f})"
                        cv2.putText(frame, text, (px + 10, py), self.font, 0.3, (0, 255, 0), 1, cv2.LINE_AA)

        # 4. Standard Metrics UI Panel
        y_offset = 30
        metrics = [
            f"FPS: {state_data.fps}",
            f"Camera: {'Connected' if state_data.camera_connected else 'Error'}",
            f"Global Tracking: {rider_state.tracking_status}",
            f"Dev Mode (D): {'ON' if state_data.developer_mode else 'OFF'}"
        ]
        
        if state_data.developer_mode and getattr(state_data, "timings", None):
            metrics.extend([
                "",
                "--- PIPELINE LATENCY (ms) ---"
            ])
            total = 0
            for k, v in state_data.timings.items():
                metrics.append(f"{k}: {v:.1f}ms")
                total += v
            metrics.append(f"TOTAL LOGIC LATENCY: {total:.1f}ms")
        
        if rider_state and state_data.developer_mode:
            # BODY SECTION
            metrics.extend([
                "",
                "--- BODY ---",
                f"Status: {rider_state.body.tracking_status}",
                f"Quality: {rider_state.body.tracking_quality:.2f}",
                f"Lean Angle: {rider_state.body.lean_angle:.1f}",
                f"Shoulder Angle: {rider_state.body.shoulder_angle:.1f}",
                f"Torso Rotation: {rider_state.body.torso_rotation:.2f}",
                f"Head Offset: {rider_state.body.head_offset[0]:.2f}, {rider_state.body.head_offset[1]:.2f}",
                f"Scale Factor: {rider_state.body.scale_factor:.3f}",
                f"Stability: {rider_state.body.upper_body_stability:.2f}"
            ])
            
            # RIGHT HAND SECTION
            if rider_state.right_hand and rider_state.right_hand.tracking_status != "NOT_TRACKED":
                metrics.extend([
                    "",
                    "--- RIGHT HAND ---",
                    f"Status: {rider_state.right_hand.tracking_status}",
                    f"Quality: {rider_state.right_hand.tracking_quality:.2f}",
                    f"Palm Pitch: {rider_state.right_hand.palm_pitch:.1f}",
                    f"Wrist Roll Est: {rider_state.right_hand.wrist_roll_estimate:.1f}",
                    f"Grip %: {rider_state.right_hand.grip_percentage:.1f}",
                    f"Openness: {rider_state.right_hand.hand_openness:.1f}"
                ])
                
            # LEFT HAND SECTION
            if rider_state.left_hand and rider_state.left_hand.tracking_status != "NOT_TRACKED":
                metrics.extend([
                    "",
                    "--- LEFT HAND ---",
                    f"Status: {rider_state.left_hand.tracking_status}",
                    f"Quality: {rider_state.left_hand.tracking_quality:.2f}",
                    f"Palm Pitch: {rider_state.left_hand.palm_pitch:.1f}",
                    f"Wrist Roll Est: {rider_state.left_hand.wrist_roll_estimate:.1f}",
                    f"Grip %: {rider_state.left_hand.grip_percentage:.1f}",
                    f"Openness: {rider_state.left_hand.hand_openness:.1f}"
                ])
        
        for text in metrics:
            cv2.putText(frame, text, (22, y_offset+2), self.font, 0.6, (0, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(frame, text, (20, y_offset), self.font, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
            y_offset += 20
            
        # 5. Throttle & Steering HUD
        if rider_state:
            h_offset = h - 80
            
            # --- Throttle ---
            throttle_pct = int(rider_state.smoothed_throttle * 100)
            t_text = f"Throttle: {throttle_pct}%"
            
            cv2.putText(frame, t_text, (w // 2 - 320, h_offset), self.font, 0.7, (0, 0, 0), 3, cv2.LINE_AA)
            cv2.putText(frame, t_text, (w // 2 - 320, h_offset), self.font, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
            
            bar_w = 250
            bar_h = 25
            bar_x = w // 2 - 320
            bar_y = h_offset + 10
            
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (50, 50, 50), -1)
            fill_w = int(bar_w * rider_state.smoothed_throttle)
            
            if throttle_pct < 50: color = (0, 255, 0)
            elif throttle_pct < 80: color = (0, 200, 255)
            else: color = (0, 0, 255)
                
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + fill_w, bar_y + bar_h), color, -1)
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (255, 255, 255), 2)

            # --- Brake ---
            b_text = f"Brake: {'ON' if rider_state.brake_applied else 'OFF'}"
            b_color = (0, 0, 255) if rider_state.brake_applied else (200, 200, 200)
            cv2.putText(frame, b_text, (w // 2 - 320, h_offset + 60), self.font, 0.7, (0, 0, 0), 3, cv2.LINE_AA)
            cv2.putText(frame, b_text, (w // 2 - 320, h_offset + 60), self.font, 0.7, b_color, 2, cv2.LINE_AA)
            
            # --- Steering ---
            steer_val = rider_state.smoothed_steering
            steer_pct = int(abs(steer_val) * 100)
            dir_str = "Left" if steer_val < 0 else "Right" if steer_val > 0 else "Center"
            s_text = f"Steering: {steer_pct}% {dir_str}"
            
            cv2.putText(frame, s_text, (w // 2 + 70, h_offset), self.font, 0.7, (0, 0, 0), 3, cv2.LINE_AA)
            cv2.putText(frame, s_text, (w // 2 + 70, h_offset), self.font, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
            
            s_bar_w = 250
            s_bar_x = w // 2 + 70
            s_bar_y = h_offset + 10
            
            cv2.rectangle(frame, (s_bar_x, s_bar_y), (s_bar_x + s_bar_w, s_bar_y + bar_h), (50, 50, 50), -1)
            
            # Center Line
            center_x = s_bar_x + s_bar_w // 2
            cv2.line(frame, (center_x, s_bar_y), (center_x, s_bar_y + bar_h), (255, 255, 255), 2)
            
            # Indicator Dot
            indicator_x = int(center_x + (steer_val * (s_bar_w // 2)))
            cv2.circle(frame, (indicator_x, s_bar_y + bar_h // 2), 10, (255, 255, 0), -1)
            
            cv2.rectangle(frame, (s_bar_x, s_bar_y), (s_bar_x + s_bar_w, s_bar_y + bar_h), (255, 255, 255), 2)
            
            # --- Calibration Status ---
            calib_text = f"Calib: {rider_state.calibration_status} (Neutral X: {rider_state.neutral_x:.2f}) [Press 'C']"
            cv2.putText(frame, calib_text, (w // 2 - 250, h - 15), self.font, 0.6, (0, 0, 0), 3, cv2.LINE_AA)
            cv2.putText(frame, calib_text, (w // 2 - 250, h - 15), self.font, 0.6, (0, 255, 255), 1, cv2.LINE_AA)

            # --- Keyboard Output ---
            if keyboard_controller and state_data.developer_mode:
                k_y_offset = 30
                k_metrics = [
                    "--- KEYBOARD ---",
                    f"UP (Throttle): {'PRESSED' if keyboard_controller.up_pressed else 'RELEASED'}",
                    f"DOWN (Brake): {'PRESSED' if keyboard_controller.down_pressed else 'RELEASED'}",
                    f"LEFT (Steer L): {'PRESSED' if keyboard_controller.left_pressed else 'RELEASED'}",
                    f"RIGHT (Steer R): {'PRESSED' if keyboard_controller.right_pressed else 'RELEASED'}"
                ]
                
                for k_text in k_metrics:
                    color = (0, 255, 0) if "PRESSED" in k_text else (200, 200, 200)
                    cv2.putText(frame, k_text, (w - 250, k_y_offset+2), self.font, 0.6, (0, 0, 0), 2, cv2.LINE_AA)
                    cv2.putText(frame, k_text, (w - 250, k_y_offset), self.font, 0.6, color, 1, cv2.LINE_AA)
                    k_y_offset += 20
