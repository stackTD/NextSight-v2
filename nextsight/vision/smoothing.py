"""
Smoothing algorithms for stable landmark tracking in NextSight v2
"""

import numpy as np
from typing import List, Optional, Dict, Any
from collections import deque
import logging


class MovingAverageFilter:
    """Moving average filter for smoothing landmark coordinates"""
    
    def __init__(self, window_size: int = 5):
        self.window_size = window_size
        self.reset()
    
    def reset(self):
        """Reset the filter state"""
        self.x_values = deque(maxlen=self.window_size)
        self.y_values = deque(maxlen=self.window_size)
        self.z_values = deque(maxlen=self.window_size)
    
    def update(self, x: float, y: float, z: float = 0.0) -> tuple:
        """
        Update filter with new values and return smoothed coordinates
        
        Args:
            x, y, z: New coordinate values
            
        Returns:
            Tuple of (smoothed_x, smoothed_y, smoothed_z)
        """
        self.x_values.append(x)
        self.y_values.append(y)
        self.z_values.append(z)
        
        # Calculate moving average
        smoothed_x = sum(self.x_values) / len(self.x_values)
        smoothed_y = sum(self.y_values) / len(self.y_values)
        smoothed_z = sum(self.z_values) / len(self.z_values)
        
        return smoothed_x, smoothed_y, smoothed_z
    
    def is_initialized(self) -> bool:
        """Check if filter has enough data"""
        return len(self.x_values) >= min(3, self.window_size)


class OneEuroFilter:
    """One Euro Filter for adaptive smoothing based on velocity"""
    
    def __init__(self, min_cutoff: float = 1.0, beta: float = 0.007, d_cutoff: float = 1.0):
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.d_cutoff = d_cutoff
        self.reset()
    
    def reset(self):
        """Reset filter state"""
        self.x_prev = None
        self.dx_prev = None
        self.timestamp_prev = None
    
    def update(self, x: float, timestamp: float) -> float:
        """
        Update filter with new value
        
        Args:
            x: New value
            timestamp: Current timestamp
            
        Returns:
            Smoothed value
        """
        if self.x_prev is None:
            self.x_prev = x
            self.timestamp_prev = timestamp
            return x
        
        # Calculate time delta
        dt = timestamp - self.timestamp_prev
        if dt <= 0:
            return self.x_prev
        
        # Calculate velocity
        dx = (x - self.x_prev) / dt
        
        # Apply filter to velocity
        if self.dx_prev is not None:
            alpha_d = self._alpha(dt, self.d_cutoff)
            dx = self.dx_prev + alpha_d * (dx - self.dx_prev)
        
        # Calculate adaptive cutoff frequency
        cutoff = self.min_cutoff + self.beta * abs(dx)
        
        # Apply filter to position
        alpha = self._alpha(dt, cutoff)
        x_filtered = self.x_prev + alpha * (x - self.x_prev)
        
        # Update state
        self.x_prev = x_filtered
        self.dx_prev = dx
        self.timestamp_prev = timestamp
        
        return x_filtered
    
    def _alpha(self, dt: float, cutoff: float) -> float:
        """Calculate alpha parameter for filter"""
        tau = 1.0 / (2 * np.pi * cutoff)
        return 1.0 / (1.0 + tau / dt)


class LandmarkSmoother:
    """Smoother for MediaPipe landmarks with multiple filtering options"""
    
    def __init__(self, 
                 filter_type: str = "moving_average",
                 window_size: int = 5,
                 confidence_threshold: float = 0.5):
        """
        Initialize landmark smoother
        
        Args:
            filter_type: "moving_average" or "one_euro"
            window_size: Size of moving average window
            confidence_threshold: Minimum confidence for using landmarks
        """
        self.filter_type = filter_type
        self.confidence_threshold = confidence_threshold
        self.filters = {}  # Dict to store filters for each landmark
        self.window_size = window_size
        self.logger = logging.getLogger(__name__)
        
        # One Euro filter parameters
        self.one_euro_params = {
            'min_cutoff': 1.0,
            'beta': 0.007,
            'd_cutoff': 1.0
        }
    
    def smooth_landmarks(self, landmarks: List[Dict], confidence: float, 
                        landmark_id: str, timestamp: float = None) -> Optional[List[Dict]]:
        """
        Smooth a set of landmarks
        
        Args:
            landmarks: List of landmark dictionaries with 'x', 'y', 'z' keys
            confidence: Detection confidence
            landmark_id: Unique identifier for this set of landmarks
            timestamp: Current timestamp (required for One Euro filter)
            
        Returns:
            Smoothed landmarks or None if confidence too low
        """
        if confidence < self.confidence_threshold:
            return None
        
        if not landmarks:
            return landmarks
        
        # Initialize filters if needed
        if landmark_id not in self.filters:
            self.filters[landmark_id] = self._create_filters(len(landmarks))
        
        smoothed_landmarks = []
        
        for i, landmark in enumerate(landmarks):
            if i >= len(self.filters[landmark_id]):
                # Add new filter if we have more landmarks than expected
                self.filters[landmark_id].extend(
                    self._create_filters(len(landmarks) - len(self.filters[landmark_id]))
                )
            
            filter_set = self.filters[landmark_id][i]
            
            if self.filter_type == "moving_average":
                smoothed_x, smoothed_y, smoothed_z = filter_set.update(
                    landmark['x'], landmark['y'], landmark.get('z', 0.0)
                )
            elif self.filter_type == "one_euro":
                if timestamp is None:
                    timestamp = 0.0  # Fallback
                
                smoothed_x = filter_set['x'].update(landmark['x'], timestamp)
                smoothed_y = filter_set['y'].update(landmark['y'], timestamp)
                smoothed_z = filter_set['z'].update(landmark.get('z', 0.0), timestamp)
            else:
                # No smoothing
                smoothed_x = landmark['x']
                smoothed_y = landmark['y']
                smoothed_z = landmark.get('z', 0.0)
            
            smoothed_landmarks.append({
                'x': smoothed_x,
                'y': smoothed_y,
                'z': smoothed_z
            })
        
        return smoothed_landmarks
    
    def _create_filters(self, num_landmarks: int) -> List:
        """Create filters for a set of landmarks"""
        if self.filter_type == "moving_average":
            return [MovingAverageFilter(self.window_size) for _ in range(num_landmarks)]
        elif self.filter_type == "one_euro":
            return [{
                'x': OneEuroFilter(**self.one_euro_params),
                'y': OneEuroFilter(**self.one_euro_params),
                'z': OneEuroFilter(**self.one_euro_params)
            } for _ in range(num_landmarks)]
        else:
            return []
    
    def reset_filters(self, landmark_id: str = None):
        """Reset filters for specific landmark set or all"""
        if landmark_id:
            if landmark_id in self.filters:
                del self.filters[landmark_id]
        else:
            self.filters.clear()
    
    def set_confidence_threshold(self, threshold: float):
        """Update confidence threshold"""
        self.confidence_threshold = max(0.0, min(1.0, threshold))
    
    def is_initialized(self, landmark_id: str) -> bool:
        """Check if filters are initialized for landmark set"""
        if landmark_id not in self.filters:
            return False
        
        if self.filter_type == "moving_average":
            return all(f.is_initialized() for f in self.filters[landmark_id])
        else:
            return True  # One Euro filter doesn't need initialization time


class ConfidenceValidator:
    """Validates detection confidence over time"""
    
    def __init__(self, min_confidence: float = 0.5, stability_window: int = 5):
        """
        Initialize confidence validator
        
        Args:
            min_confidence: Minimum confidence threshold
            stability_window: Number of frames to track for stability
        """
        self.min_confidence = min_confidence
        self.stability_window = stability_window
        self.confidence_history = deque(maxlen=stability_window)
        
    def validate(self, confidence: float) -> bool:
        """
        Validate confidence and return if detection is stable
        
        Args:
            confidence: Current detection confidence
            
        Returns:
            True if detection is considered stable and valid
        """
        self.confidence_history.append(confidence)
        
        # Check immediate confidence
        if confidence < self.min_confidence:
            return False
        
        # Check stability over time
        if len(self.confidence_history) >= self.stability_window:
            avg_confidence = sum(self.confidence_history) / len(self.confidence_history)
            return avg_confidence >= self.min_confidence
        
        # Not enough history yet, use current confidence
        return confidence >= self.min_confidence
    
    def get_stability_score(self) -> float:
        """Get current stability score (0.0 to 1.0)"""
        if not self.confidence_history:
            return 0.0
        
        return sum(self.confidence_history) / len(self.confidence_history)
    
    def reset(self):
        """Reset confidence history"""
        self.confidence_history.clear()