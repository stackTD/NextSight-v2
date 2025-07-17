"""
Enhanced MediaPipe hand tracking module for NextSight v2
Multi-hand detection with smoothing and improved accuracy
"""

import cv2
import mediapipe as mp
import numpy as np
import time
from typing import Optional, List, Tuple, Dict
from nextsight.vision.smoothing import LandmarkSmoother, ConfidenceValidator
from nextsight.utils.config import config
import logging


class HandTracker:
    """Professional hand tracking using MediaPipe Hands with enhanced features"""
    
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Initialize hands solution
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=config.hand_detection.max_num_hands,
            min_detection_confidence=config.hand_detection.confidence_threshold,
            min_tracking_confidence=config.hand_detection.tracking_confidence,
            model_complexity=config.hand_detection.model_complexity
        )
        
        # State management
        self.detection_enabled = True
        self.landmarks_visible = True
        self.connections_visible = True
        self.gesture_recognition_enabled = False
        
        # Enhanced tracking features
        self.smoother = LandmarkSmoother(
            filter_type="moving_average",
            window_size=5,
            confidence_threshold=config.hand_detection.confidence_threshold
        )
        
        # Separate confidence validators for each hand
        self.left_hand_validator = ConfidenceValidator(
            min_confidence=config.hand_detection.confidence_threshold,
            stability_window=5
        )
        self.right_hand_validator = ConfidenceValidator(
            min_confidence=config.hand_detection.confidence_threshold,
            stability_window=5
        )
        
        # Hand tracking state
        self.hand_states = {
            'left': {'present': False, 'stable': False, 'last_seen': 0},
            'right': {'present': False, 'stable': False, 'last_seen': 0}
        }
        
        # Hand zones for interaction (to be used in Phase 3)
        self.hand_zones = {
            'left': None,
            'right': None
        }
        
        self.logger = logging.getLogger(__name__)
        
    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, dict]:
        """
        Process a frame for enhanced hand detection
        
        Args:
            frame: Input BGR frame
            
        Returns:
            Tuple of (processed_frame, detection_info)
        """
        if not self.detection_enabled:
            return frame, {}
            
        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame
        results = self.hands.process(rgb_frame)
        
        # Prepare enhanced detection info
        detection_info = {
            'hands_detected': 0,
            'hand_landmarks': [],
            'handedness': [],
            'hand_confidences': [],
            'stable_hands': [],
            'hand_zones': {},
            'left_hand': {'present': False, 'landmarks': None, 'confidence': 0.0},
            'right_hand': {'present': False, 'landmarks': None, 'confidence': 0.0}
        }
        
        current_time = time.time()
        
        # Process detected hands
        if results.multi_hand_landmarks and results.multi_handedness:
            detection_info['hands_detected'] = len(results.multi_hand_landmarks)
            
            for idx, (hand_landmarks, handedness) in enumerate(
                zip(results.multi_hand_landmarks, results.multi_handedness)
            ):
                # Get hand label and confidence
                hand_label = handedness.classification[0].label  # 'Left' or 'Right'
                hand_confidence = handedness.classification[0].score
                hand_side = hand_label.lower()
                
                # Validate confidence with appropriate validator
                validator = self.left_hand_validator if hand_side == 'left' else self.right_hand_validator
                is_stable = validator.validate(hand_confidence)
                
                # Extract landmark data
                landmarks_list = []
                for landmark in hand_landmarks.landmark:
                    landmarks_list.append({
                        'x': landmark.x,
                        'y': landmark.y,
                        'z': landmark.z
                    })
                
                # Apply smoothing
                smoothed_landmarks = self.smoother.smooth_landmarks(
                    landmarks_list, hand_confidence, f"hand_{hand_side}", current_time
                )
                
                if smoothed_landmarks and is_stable:
                    # Update detection info
                    detection_info['hand_landmarks'].append(smoothed_landmarks)
                    detection_info['handedness'].append(hand_label)
                    detection_info['hand_confidences'].append(hand_confidence)
                    detection_info['stable_hands'].append(hand_side)
                    
                    # Update specific hand info
                    detection_info[f'{hand_side}_hand'] = {
                        'present': True,
                        'landmarks': smoothed_landmarks,
                        'confidence': hand_confidence
                    }
                    
                    # Update hand state
                    self.hand_states[hand_side] = {
                        'present': True,
                        'stable': is_stable,
                        'last_seen': current_time
                    }
                    
                    # Calculate hand zone (center of palm)
                    self._calculate_hand_zone(smoothed_landmarks, hand_side, detection_info)
                    
                    # Draw enhanced annotations
                    if self.landmarks_visible or self.connections_visible:
                        self._draw_enhanced_hand_landmarks(
                            frame, hand_landmarks, hand_label, hand_confidence, is_stable
                        )
                else:
                    # Mark hand as not stable
                    self.hand_states[hand_side]['stable'] = False
        
        # Update missing hands
        for hand_side in ['left', 'right']:
            if hand_side not in [h.lower() for h in detection_info['handedness']]:
                self.hand_states[hand_side]['present'] = False
                detection_info[f'{hand_side}_hand']['present'] = False
        
        return frame, detection_info
    
    def _calculate_hand_zone(self, landmarks: List[Dict], hand_side: str, detection_info: dict):
        """Calculate hand interaction zone"""
        if not landmarks or len(landmarks) < 21:
            return
        
        # Use wrist (0) and middle finger MCP (9) to calculate palm center
        wrist = landmarks[0]
        mcp = landmarks[9]
        
        palm_center_x = (wrist['x'] + mcp['x']) / 2
        palm_center_y = (wrist['y'] + mcp['y']) / 2
        
        zone_info = {
            'center': {'x': palm_center_x, 'y': palm_center_y},
            'wrist': wrist,
            'fingertips': {
                'thumb': landmarks[4],
                'index': landmarks[8],
                'middle': landmarks[12],
                'ring': landmarks[16],
                'pinky': landmarks[20]
            }
        }
        
        detection_info['hand_zones'][hand_side] = zone_info
        self.hand_zones[hand_side] = zone_info
    
    def _draw_enhanced_hand_landmarks(self, frame: np.ndarray, hand_landmarks, 
                                    hand_label: str, confidence: float, is_stable: bool):
        """Draw enhanced hand landmarks with improved visualization"""
        h, w, _ = frame.shape
        
        # Choose colors based on stability and confidence
        if is_stable and confidence > 0.8:
            landmark_color = (0, 255, 0)  # Green for stable high confidence
            connection_color = (0, 200, 0)
            text_color = (0, 255, 0)
        elif is_stable:
            landmark_color = (0, 255, 255)  # Yellow for stable medium confidence
            connection_color = (0, 200, 200)
            text_color = (0, 255, 255)
        else:
            landmark_color = (0, 100, 255)  # Orange for unstable
            connection_color = (0, 100, 200)
            text_color = (0, 150, 255)
        
        # Draw connections
        if self.connections_visible:
            self.mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                self.mp_hands.HAND_CONNECTIONS,
                landmark_drawing_spec=self.mp_drawing.DrawingSpec(
                    color=landmark_color, thickness=2, circle_radius=2
                ),
                connection_drawing_spec=self.mp_drawing.DrawingSpec(
                    color=connection_color, thickness=2
                )
            )
        elif self.landmarks_visible:
            # Draw only landmarks without connections
            self.mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                None,  # No connections
                landmark_drawing_spec=self.mp_drawing.DrawingSpec(
                    color=landmark_color, thickness=2, circle_radius=3
                )
            )
        
        # Enhanced hand label with stability indicator
        if hand_landmarks.landmark:
            # Position label near wrist
            wrist = hand_landmarks.landmark[0]
            label_x = int(wrist.x * w)
            label_y = int(wrist.y * h) + 30
            
            # Create enhanced label
            stability_indicator = "●" if is_stable else "○"
            label_text = f"{hand_label} {stability_indicator} {confidence:.2f}"
            
            # Draw background for text
            text_size = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
            cv2.rectangle(frame, 
                         (label_x - 5, label_y - text_size[1] - 5),
                         (label_x + text_size[0] + 5, label_y + 5),
                         (0, 0, 0), -1)
            
            # Draw text
            cv2.putText(frame, label_text,
                       (label_x, label_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 2)
    
    def toggle_detection(self) -> bool:
        """Toggle hand detection on/off"""
        self.detection_enabled = not self.detection_enabled
        if not self.detection_enabled:
            self._reset_tracking_state()
        self.logger.info(f"Hand detection {'enabled' if self.detection_enabled else 'disabled'}")
        return self.detection_enabled
    
    def toggle_landmarks(self) -> bool:
        """Toggle landmark visibility"""
        self.landmarks_visible = not self.landmarks_visible
        self.logger.info(f"Hand landmarks {'enabled' if self.landmarks_visible else 'disabled'}")
        return self.landmarks_visible
    
    def toggle_connections(self) -> bool:
        """Toggle connection lines visibility"""
        self.connections_visible = not self.connections_visible
        self.logger.info(f"Hand connections {'enabled' if self.connections_visible else 'disabled'}")
        return self.connections_visible
    
    def toggle_gesture_recognition(self) -> bool:
        """Toggle gesture recognition on/off"""
        self.gesture_recognition_enabled = not self.gesture_recognition_enabled
        self.logger.info(f"Gesture recognition {'enabled' if self.gesture_recognition_enabled else 'disabled'}")
        return self.gesture_recognition_enabled
    
    def set_confidence_threshold(self, threshold: float):
        """Update confidence threshold"""
        if 0.0 <= threshold <= 1.0:
            config.hand_detection.confidence_threshold = threshold
            self.smoother.set_confidence_threshold(threshold)
            self.left_hand_validator.min_confidence = threshold
            self.right_hand_validator.min_confidence = threshold
            
            # Reinitialize with new settings
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=config.hand_detection.max_num_hands,
                min_detection_confidence=threshold,
                min_tracking_confidence=config.hand_detection.tracking_confidence,
                model_complexity=config.hand_detection.model_complexity
            )
            self.logger.info(f"Hand confidence threshold set to {threshold:.2f}")
    
    def get_detection_stats(self) -> dict:
        """Get enhanced detection statistics"""
        return {
            'detection_enabled': self.detection_enabled,
            'landmarks_visible': self.landmarks_visible,
            'connections_visible': self.connections_visible,
            'gesture_recognition_enabled': self.gesture_recognition_enabled,
            'confidence_threshold': config.hand_detection.confidence_threshold,
            'tracking_confidence': config.hand_detection.tracking_confidence,
            'max_hands': config.hand_detection.max_num_hands,
            'left_hand_stable': self.hand_states['left']['stable'],
            'right_hand_stable': self.hand_states['right']['stable'],
            'left_hand_stability': self.left_hand_validator.get_stability_score(),
            'right_hand_stability': self.right_hand_validator.get_stability_score()
        }
    
    def get_hand_zones(self) -> dict:
        """Get current hand interaction zones"""
        return self.hand_zones.copy()
    
    def is_hand_stable(self, hand_side: str) -> bool:
        """Check if specific hand tracking is stable"""
        return self.hand_states.get(hand_side, {}).get('stable', False)
    
    def _reset_tracking_state(self):
        """Reset all tracking state"""
        for hand_side in ['left', 'right']:
            self.hand_states[hand_side] = {
                'present': False,
                'stable': False,
                'last_seen': 0
            }
            self.hand_zones[hand_side] = None
        
        self.smoother.reset_filters()
        self.left_hand_validator.reset()
        self.right_hand_validator.reset()
    
    def cleanup(self):
        """Cleanup resources"""
        if hasattr(self, 'hands'):
            self.hands.close()
        self._reset_tracking_state()
        self.logger.info("Hand tracker cleaned up")