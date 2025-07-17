"""
MediaPipe hand detection module for NextSight v2
"""

import cv2
import mediapipe as mp
import numpy as np
from typing import Optional, List, Tuple
from nextsight.utils.config import config


class HandDetector:
    """Professional hand detection using MediaPipe"""
    
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
        
        self.detection_enabled = True
        self.landmarks_visible = True
        self.connections_visible = True
        
    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, dict]:
        """
        Process a frame for hand detection
        
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
        
        # Prepare detection info
        detection_info = {
            'hands_detected': 0,
            'hand_landmarks': [],
            'handedness': []
        }
        
        # Draw annotations if hands are detected
        if results.multi_hand_landmarks:
            detection_info['hands_detected'] = len(results.multi_hand_landmarks)
            
            for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # Store landmark data
                landmarks_list = []
                for landmark in hand_landmarks.landmark:
                    landmarks_list.append({
                        'x': landmark.x,
                        'y': landmark.y,
                        'z': landmark.z
                    })
                detection_info['hand_landmarks'].append(landmarks_list)
                
                # Store handedness if available
                if results.multi_handedness and idx < len(results.multi_handedness):
                    handedness = results.multi_handedness[idx].classification[0].label
                    detection_info['handedness'].append(handedness)
                
                # Draw landmarks and connections
                if self.landmarks_visible:
                    self.mp_drawing.draw_landmarks(
                        frame,
                        hand_landmarks,
                        self.mp_hands.HAND_CONNECTIONS if self.connections_visible else None,
                        self.mp_drawing_styles.get_default_hand_landmarks_style(),
                        self.mp_drawing_styles.get_default_hand_connections_style()
                    )
                
                # Add hand label
                if detection_info['handedness']:
                    h, w, _ = frame.shape
                    cx = int(hand_landmarks.landmark[9].x * w)  # Middle finger MCP
                    cy = int(hand_landmarks.landmark[9].y * h)
                    
                    label = detection_info['handedness'][idx] if idx < len(detection_info['handedness']) else f"Hand {idx+1}"
                    
                    # Draw background rectangle for text
                    text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                    cv2.rectangle(frame, 
                                (cx - text_size[0]//2 - 5, cy - 25),
                                (cx + text_size[0]//2 + 5, cy - 5),
                                (0, 0, 0), -1)
                    
                    # Draw text
                    cv2.putText(frame, label,
                              (cx - text_size[0]//2, cy - 10),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        return frame, detection_info
    
    def toggle_detection(self) -> bool:
        """Toggle hand detection on/off"""
        self.detection_enabled = not self.detection_enabled
        return self.detection_enabled
    
    def toggle_landmarks(self) -> bool:
        """Toggle landmark visibility"""
        self.landmarks_visible = not self.landmarks_visible
        return self.landmarks_visible
    
    def toggle_connections(self) -> bool:
        """Toggle connection lines visibility"""
        self.connections_visible = not self.connections_visible
        return self.connections_visible
    
    def set_confidence_threshold(self, threshold: float):
        """Update confidence threshold"""
        if 0.0 <= threshold <= 1.0:
            config.hand_detection.confidence_threshold = threshold
            # Reinitialize with new settings
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=config.hand_detection.max_num_hands,
                min_detection_confidence=threshold,
                min_tracking_confidence=config.hand_detection.tracking_confidence,
                model_complexity=config.hand_detection.model_complexity
            )
    
    def get_detection_stats(self) -> dict:
        """Get current detection statistics"""
        return {
            'detection_enabled': self.detection_enabled,
            'landmarks_visible': self.landmarks_visible,
            'connections_visible': self.connections_visible,
            'confidence_threshold': config.hand_detection.confidence_threshold,
            'tracking_confidence': config.hand_detection.tracking_confidence,
            'max_hands': config.hand_detection.max_num_hands
        }
    
    def cleanup(self):
        """Cleanup resources"""
        if hasattr(self, 'hands'):
            self.hands.close()