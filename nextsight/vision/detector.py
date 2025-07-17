"""
Main detection coordinator for NextSight v2
Manages both hand tracking and pose detection with enhanced features
"""

import cv2
import numpy as np
import time
from typing import Tuple, Dict
from nextsight.vision.hand_tracker import HandTracker
from nextsight.vision.pose_detector import PoseDetector
from nextsight.utils.config import config
import logging


class MultiModalDetector:
    """Coordinates hand tracking and pose detection for professional exhibition demo"""
    
    def __init__(self):
        # Initialize detection modules
        self.hand_tracker = HandTracker()
        self.pose_detector = PoseDetector()
        
        # Detection state
        self.hand_detection_enabled = True
        self.pose_detection_enabled = True
        
        # Performance tracking
        self.frame_count = 0
        self.last_fps_time = time.time()
        self.processing_times = []
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("MultiModal detector initialized")
    
    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, dict]:
        """
        Process frame with both hand and pose detection
        
        Args:
            frame: Input BGR frame
            
        Returns:
            Tuple of (processed_frame, combined_detection_info)
        """
        start_time = time.time()
        processed_frame = frame.copy()
        
        # Combined detection info
        detection_info = {
            'timestamp': start_time,
            'frame_number': self.frame_count,
            'hands': {},
            'pose': {},
            'combined_confidence': 0.0,
            'performance': {}
        }
        
        # Process hands if enabled
        if self.hand_detection_enabled:
            hand_start = time.time()
            processed_frame, hand_info = self.hand_tracker.process_frame(processed_frame)
            hand_time = time.time() - hand_start
            
            detection_info['hands'] = hand_info
            detection_info['performance']['hand_processing_time'] = hand_time
        
        # Process pose if enabled
        if self.pose_detection_enabled:
            pose_start = time.time()
            processed_frame, pose_info = self.pose_detector.process_frame(processed_frame)
            pose_time = time.time() - pose_start
            
            detection_info['pose'] = pose_info
            detection_info['performance']['pose_processing_time'] = pose_time
        
        # Calculate combined confidence
        self._calculate_combined_confidence(detection_info)
        
        # Add performance overlay
        self._add_performance_overlay(processed_frame, detection_info)
        
        # Update performance tracking
        total_time = time.time() - start_time
        self.processing_times.append(total_time)
        if len(self.processing_times) > 30:
            self.processing_times.pop(0)
        
        detection_info['performance']['total_processing_time'] = total_time
        self.frame_count += 1
        
        return processed_frame, detection_info
    
    def _calculate_combined_confidence(self, detection_info: dict):
        """Calculate overall detection confidence"""
        hand_confidence = 0.0
        pose_confidence = 0.0
        
        # Get hand confidence
        if 'hands' in detection_info and detection_info['hands'].get('hand_confidences'):
            hand_confidence = max(detection_info['hands']['hand_confidences'])
        
        # Get pose confidence
        if 'pose' in detection_info:
            pose_confidence = detection_info['pose'].get('pose_confidence', 0.0)
        
        # Combined confidence (weighted average)
        if self.hand_detection_enabled and self.pose_detection_enabled:
            detection_info['combined_confidence'] = (hand_confidence + pose_confidence) / 2
        elif self.hand_detection_enabled:
            detection_info['combined_confidence'] = hand_confidence
        elif self.pose_detection_enabled:
            detection_info['combined_confidence'] = pose_confidence
        else:
            detection_info['combined_confidence'] = 0.0
    
    def _add_performance_overlay(self, frame: np.ndarray, detection_info: dict):
        """Add performance information overlay"""
        h, w, _ = frame.shape
        
        # Performance stats
        avg_processing_time = sum(self.processing_times) / len(self.processing_times) if self.processing_times else 0
        estimated_fps = 1.0 / avg_processing_time if avg_processing_time > 0 else 0
        
        # Status indicators
        y_offset = 20
        
        # Detection status
        hand_status = "ON" if self.hand_detection_enabled else "OFF"
        pose_status = "ON" if self.pose_detection_enabled else "OFF"
        
        hand_color = (0, 255, 0) if self.hand_detection_enabled else (0, 0, 255)
        pose_color = (0, 255, 0) if self.pose_detection_enabled else (0, 0, 255)
        
        cv2.putText(frame, f"Hands: {hand_status}", (10, y_offset), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, hand_color, 2)
        y_offset += 25
        
        cv2.putText(frame, f"Pose: {pose_status}", (10, y_offset), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, pose_color, 2)
        y_offset += 25
        
        # Performance info
        if estimated_fps > 0:
            fps_color = (0, 255, 0) if estimated_fps >= 30 else (0, 255, 255) if estimated_fps >= 20 else (0, 0, 255)
            # cv2.putText(frame, f"FPS: {estimated_fps:.1f}", (10, y_offset), 
            #            cv2.FONT_HERSHEY_SIMPLEX, 0.6, fps_color, 2)
    
    # Hand detection controls
    def toggle_hand_detection(self) -> bool:
        """Toggle hand detection on/off"""
        self.hand_detection_enabled = not self.hand_detection_enabled
        if not self.hand_detection_enabled:
            # Keep tracker instance but disable processing
            pass
        self.logger.info(f"Hand detection {'enabled' if self.hand_detection_enabled else 'disabled'}")
        return self.hand_detection_enabled
    
    def toggle_hand_landmarks(self) -> bool:
        """Toggle hand landmark visibility"""
        return self.hand_tracker.toggle_landmarks()
    
    def toggle_hand_connections(self) -> bool:
        """Toggle hand connection lines"""
        return self.hand_tracker.toggle_connections()
    
    def toggle_gesture_recognition(self) -> bool:
        """Toggle gesture recognition"""
        return self.hand_tracker.toggle_gesture_recognition()
    
    # Pose detection controls
    def toggle_pose_detection(self) -> bool:
        """Toggle pose detection on/off"""
        self.pose_detection_enabled = not self.pose_detection_enabled
        if not self.pose_detection_enabled:
            # Keep detector instance but disable processing
            pass
        self.logger.info(f"Pose detection {'enabled' if self.pose_detection_enabled else 'disabled'}")
        return self.pose_detection_enabled
    
    def toggle_pose_landmarks(self) -> bool:
        """Toggle pose landmark visibility"""
        return self.pose_detector.toggle_landmarks()
    
    def toggle_pose_connections(self) -> bool:
        """Toggle pose connection lines"""
        return self.pose_detector.toggle_connections()
    
    # Combined controls
    def set_confidence_threshold(self, threshold: float):
        """Set confidence threshold for both detectors"""
        self.hand_tracker.set_confidence_threshold(threshold)
        self.pose_detector.set_confidence_threshold(threshold)
    
    def reset_detection_settings(self):
        """Reset all detection settings to defaults"""
        self.hand_detection_enabled = True
        self.pose_detection_enabled = True
        
        # Reset individual detectors
        self.hand_tracker.detection_enabled = True
        self.hand_tracker.landmarks_visible = True
        self.hand_tracker.connections_visible = True
        self.hand_tracker.gesture_recognition_enabled = False
        
        self.pose_detector.detection_enabled = True
        self.pose_detector.landmarks_visible = True
        self.pose_detector.connections_visible = True
        
        self.logger.info("Detection settings reset to defaults")
    
    def get_detection_stats(self) -> dict:
        """Get comprehensive detection statistics"""
        hand_stats = self.hand_tracker.get_detection_stats()
        pose_stats = self.pose_detector.get_detection_stats()
        
        avg_processing_time = sum(self.processing_times) / len(self.processing_times) if self.processing_times else 0
        estimated_fps = 1.0 / avg_processing_time if avg_processing_time > 0 else 0
        
        return {
            'hand_detection_enabled': self.hand_detection_enabled,
            'pose_detection_enabled': self.pose_detection_enabled,
            'hand_stats': hand_stats,
            'pose_stats': pose_stats,
            'performance': {
                'estimated_fps': estimated_fps,
                'avg_processing_time': avg_processing_time,
                'frame_count': self.frame_count
            }
        }
    
    def cleanup(self):
        """Cleanup all resources"""
        self.hand_tracker.cleanup()
        self.pose_detector.cleanup()
        self.logger.info("MultiModal detector cleaned up")


# Maintain backward compatibility
class HandDetector(MultiModalDetector):
    """Backward compatibility wrapper"""
    
    def __init__(self):
        super().__init__()
        # For backward compatibility, start with only hand detection
        self.pose_detection_enabled = False
    
    def toggle_detection(self) -> bool:
        """Legacy method - toggles hand detection"""
        return self.toggle_hand_detection()
    
    def toggle_landmarks(self) -> bool:
        """Legacy method - toggles hand landmarks"""
        return self.toggle_hand_landmarks()
    
    def toggle_connections(self) -> bool:
        """Legacy method - toggles hand connections"""
        return self.toggle_hand_connections()