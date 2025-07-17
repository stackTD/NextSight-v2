"""
MediaPipe pose detection module for NextSight v2
Focus on upper body tracking with torso, shoulders, arms, and elbow landmarks
"""

import cv2
import mediapipe as mp
import numpy as np
import time
from typing import Optional, List, Tuple, Dict
from nextsight.vision.smoothing import LandmarkSmoother, ConfidenceValidator
from nextsight.utils.config import config
import logging


class PoseDetector:
    """Professional pose detection using MediaPipe Pose"""
    
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Initialize pose solution
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,  # Balance between accuracy and performance
            enable_segmentation=False,  # Disable segmentation for better performance
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # State management
        self.detection_enabled = True
        self.landmarks_visible = True
        self.connections_visible = True
        
        # Smoothing and validation
        self.smoother = LandmarkSmoother(
            filter_type="moving_average",
            window_size=5,
            confidence_threshold=0.5
        )
        self.confidence_validator = ConfidenceValidator(
            min_confidence=0.5,
            stability_window=5
        )
        
        # Focus on upper body landmarks
        self.upper_body_landmarks = [
            self.mp_pose.PoseLandmark.NOSE,
            self.mp_pose.PoseLandmark.LEFT_EYE_INNER,
            self.mp_pose.PoseLandmark.LEFT_EYE,
            self.mp_pose.PoseLandmark.LEFT_EYE_OUTER,
            self.mp_pose.PoseLandmark.RIGHT_EYE_INNER,
            self.mp_pose.PoseLandmark.RIGHT_EYE,
            self.mp_pose.PoseLandmark.RIGHT_EYE_OUTER,
            self.mp_pose.PoseLandmark.LEFT_EAR,
            self.mp_pose.PoseLandmark.RIGHT_EAR,
            self.mp_pose.PoseLandmark.MOUTH_LEFT,
            self.mp_pose.PoseLandmark.MOUTH_RIGHT,
            self.mp_pose.PoseLandmark.LEFT_SHOULDER,
            self.mp_pose.PoseLandmark.RIGHT_SHOULDER,
            self.mp_pose.PoseLandmark.LEFT_ELBOW,
            self.mp_pose.PoseLandmark.RIGHT_ELBOW,
            self.mp_pose.PoseLandmark.LEFT_WRIST,
            self.mp_pose.PoseLandmark.RIGHT_WRIST,
            self.mp_pose.PoseLandmark.LEFT_HIP,
            self.mp_pose.PoseLandmark.RIGHT_HIP,
        ]
        
        # Upper body connections for visualization
        self.upper_body_connections = [
            # Face
            (self.mp_pose.PoseLandmark.LEFT_EYE_INNER, self.mp_pose.PoseLandmark.LEFT_EYE),
            (self.mp_pose.PoseLandmark.LEFT_EYE, self.mp_pose.PoseLandmark.LEFT_EYE_OUTER),
            (self.mp_pose.PoseLandmark.RIGHT_EYE_INNER, self.mp_pose.PoseLandmark.RIGHT_EYE),
            (self.mp_pose.PoseLandmark.RIGHT_EYE, self.mp_pose.PoseLandmark.RIGHT_EYE_OUTER),
            (self.mp_pose.PoseLandmark.LEFT_EAR, self.mp_pose.PoseLandmark.LEFT_EYE_OUTER),
            (self.mp_pose.PoseLandmark.RIGHT_EAR, self.mp_pose.PoseLandmark.RIGHT_EYE_OUTER),
            (self.mp_pose.PoseLandmark.MOUTH_LEFT, self.mp_pose.PoseLandmark.MOUTH_RIGHT),
            
            # Torso and arms
            (self.mp_pose.PoseLandmark.LEFT_SHOULDER, self.mp_pose.PoseLandmark.RIGHT_SHOULDER),
            (self.mp_pose.PoseLandmark.LEFT_SHOULDER, self.mp_pose.PoseLandmark.LEFT_ELBOW),
            (self.mp_pose.PoseLandmark.LEFT_ELBOW, self.mp_pose.PoseLandmark.LEFT_WRIST),
            (self.mp_pose.PoseLandmark.RIGHT_SHOULDER, self.mp_pose.PoseLandmark.RIGHT_ELBOW),
            (self.mp_pose.PoseLandmark.RIGHT_ELBOW, self.mp_pose.PoseLandmark.RIGHT_WRIST),
            (self.mp_pose.PoseLandmark.LEFT_SHOULDER, self.mp_pose.PoseLandmark.LEFT_HIP),
            (self.mp_pose.PoseLandmark.RIGHT_SHOULDER, self.mp_pose.PoseLandmark.RIGHT_HIP),
            (self.mp_pose.PoseLandmark.LEFT_HIP, self.mp_pose.PoseLandmark.RIGHT_HIP),
        ]
        
        self.logger = logging.getLogger(__name__)
        
    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, dict]:
        """
        Process a frame for pose detection
        
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
        results = self.pose.process(rgb_frame)
        
        # Prepare detection info
        detection_info = {
            'pose_detected': False,
            'pose_landmarks': [],
            'upper_body_landmarks': [],
            'pose_confidence': 0.0,
            'pose_visibility': []
        }
        
        current_time = time.time()
        
        # Process pose landmarks if detected
        if results.pose_landmarks:
            # Calculate overall confidence
            landmarks = results.pose_landmarks.landmark
            visibilities = [landmark.visibility for landmark in landmarks]
            avg_visibility = sum(visibilities) / len(visibilities) if visibilities else 0.0
            
            # Validate confidence
            if self.confidence_validator.validate(avg_visibility):
                detection_info['pose_detected'] = True
                detection_info['pose_confidence'] = avg_visibility
                
                # Extract landmark data
                landmarks_list = []
                upper_body_list = []
                visibility_list = []
                
                for i, landmark in enumerate(landmarks):
                    landmark_data = {
                        'x': landmark.x,
                        'y': landmark.y,
                        'z': landmark.z,
                        'visibility': landmark.visibility
                    }
                    landmarks_list.append(landmark_data)
                    visibility_list.append(landmark.visibility)
                    
                    # Check if this is an upper body landmark
                    if i in [landmark.value for landmark in self.upper_body_landmarks]:
                        upper_body_list.append(landmark_data)
                
                # Apply smoothing
                smoothed_landmarks = self.smoother.smooth_landmarks(
                    landmarks_list, avg_visibility, "pose", current_time
                )
                
                if smoothed_landmarks:
                    detection_info['pose_landmarks'] = smoothed_landmarks
                    
                    # Extract smoothed upper body landmarks
                    smoothed_upper_body = []
                    for i, landmark in enumerate(smoothed_landmarks):
                        if i in [landmark.value for landmark in self.upper_body_landmarks]:
                            smoothed_upper_body.append(landmark)
                    
                    detection_info['upper_body_landmarks'] = smoothed_upper_body
                    detection_info['pose_visibility'] = visibility_list
                    
                    # Draw pose annotations
                    if self.landmarks_visible or self.connections_visible:
                        self._draw_pose_landmarks(frame, results.pose_landmarks, avg_visibility)
                
        return frame, detection_info
    
    def _draw_pose_landmarks(self, frame: np.ndarray, pose_landmarks, confidence: float):
        """Draw pose landmarks and connections on frame"""
        if not pose_landmarks:
            return
        
        h, w, _ = frame.shape
        
        # Choose colors based on confidence
        if confidence > 0.8:
            landmark_color = (0, 255, 0)  # Green for high confidence
            connection_color = (0, 200, 0)
        elif confidence > 0.6:
            landmark_color = (0, 255, 255)  # Yellow for medium confidence
            connection_color = (0, 200, 200)
        else:
            landmark_color = (0, 100, 255)  # Orange for low confidence
            connection_color = (0, 100, 200)
        
        # Draw connections first (so landmarks appear on top)
        if self.connections_visible:
            for connection in self.upper_body_connections:
                start_idx = connection[0].value
                end_idx = connection[1].value
                
                start_landmark = pose_landmarks.landmark[start_idx]
                end_landmark = pose_landmarks.landmark[end_idx]
                
                # Only draw if both landmarks are visible enough
                if (start_landmark.visibility > 0.5 and end_landmark.visibility > 0.5):
                    start_point = (int(start_landmark.x * w), int(start_landmark.y * h))
                    end_point = (int(end_landmark.x * w), int(end_landmark.y * h))
                    
                    cv2.line(frame, start_point, end_point, connection_color, 2)
        
        # Draw landmarks
        if self.landmarks_visible:
            for i, landmark in enumerate(pose_landmarks.landmark):
                # Only draw upper body landmarks
                if i in [landmark.value for landmark in self.upper_body_landmarks]:
                    if landmark.visibility > 0.5:
                        x = int(landmark.x * w)
                        y = int(landmark.y * h)
                        
                        # Draw landmark point
                        cv2.circle(frame, (x, y), 4, landmark_color, -1)
                        cv2.circle(frame, (x, y), 5, (255, 255, 255), 1)
        
        # Add pose confidence indicator
        self._draw_confidence_indicator(frame, confidence)
    
    def _draw_confidence_indicator(self, frame: np.ndarray, confidence: float):
        """Draw pose confidence indicator"""
        h, w, _ = frame.shape
        
        # Confidence bar
        bar_width = 200
        bar_height = 20
        bar_x = w - bar_width - 20
        bar_y = 60
        
        # Background
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (50, 50, 50), -1)
        
        # Confidence fill
        fill_width = int(bar_width * confidence)
        if confidence > 0.8:
            color = (0, 255, 0)  # Green
        elif confidence > 0.6:
            color = (0, 255, 255)  # Yellow
        else:
            color = (0, 100, 255)  # Orange
        
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + fill_width, bar_y + bar_height), color, -1)
        
        # Border
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (255, 255, 255), 1)
        
        # Text
        conf_text = f"Pose: {confidence:.2f}"
        cv2.putText(frame, conf_text, (bar_x, bar_y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    def toggle_detection(self) -> bool:
        """Toggle pose detection on/off"""
        self.detection_enabled = not self.detection_enabled
        if not self.detection_enabled:
            self.smoother.reset_filters("pose")
            self.confidence_validator.reset()
        self.logger.info(f"Pose detection {'enabled' if self.detection_enabled else 'disabled'}")
        return self.detection_enabled
    
    def toggle_landmarks(self) -> bool:
        """Toggle landmark visibility"""
        self.landmarks_visible = not self.landmarks_visible
        self.logger.info(f"Pose landmarks {'enabled' if self.landmarks_visible else 'disabled'}")
        return self.landmarks_visible
    
    def toggle_connections(self) -> bool:
        """Toggle connection lines visibility"""
        self.connections_visible = not self.connections_visible
        self.logger.info(f"Pose connections {'enabled' if self.connections_visible else 'disabled'}")
        return self.connections_visible
    
    def set_confidence_threshold(self, threshold: float):
        """Update confidence threshold"""
        if 0.0 <= threshold <= 1.0:
            self.smoother.set_confidence_threshold(threshold)
            self.confidence_validator.min_confidence = threshold
            
            # Reinitialize pose solution with new confidence
            self.pose = self.mp_pose.Pose(
                static_image_mode=False,
                model_complexity=1,
                enable_segmentation=False,
                min_detection_confidence=threshold,
                min_tracking_confidence=threshold
            )
            self.logger.info(f"Pose confidence threshold set to {threshold:.2f}")
    
    def get_detection_stats(self) -> dict:
        """Get current detection statistics"""
        return {
            'detection_enabled': self.detection_enabled,
            'landmarks_visible': self.landmarks_visible,
            'connections_visible': self.connections_visible,
            'confidence_threshold': self.confidence_validator.min_confidence,
            'stability_score': self.confidence_validator.get_stability_score(),
            'upper_body_landmarks_count': len(self.upper_body_landmarks)
        }
    
    def is_detection_stable(self) -> bool:
        """Check if pose detection is currently stable"""
        return self.confidence_validator.get_stability_score() > 0.6
    
    def cleanup(self):
        """Cleanup resources"""
        if hasattr(self, 'pose'):
            self.pose.close()
        self.smoother.reset_filters()
        self.confidence_validator.reset()
        self.logger.info("Pose detector cleaned up")