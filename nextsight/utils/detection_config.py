"""
Detection configuration for NextSight v2 Phase 2
Professional settings for hand and pose detection
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class DetectionConfig:
    """Configuration for detection modules"""
    
    # Hand detection settings
    hand_detection_enabled: bool = True
    hand_max_num_hands: int = 2
    hand_confidence_threshold: float = 0.5
    hand_tracking_confidence: float = 0.5
    hand_model_complexity: int = 1
    
    # Pose detection settings
    pose_detection_enabled: bool = True
    pose_confidence_threshold: float = 0.5
    pose_tracking_confidence: float = 0.5
    pose_model_complexity: int = 1
    
    # Smoothing settings
    smoothing_enabled: bool = True
    smoothing_window_size: int = 5
    smoothing_filter_type: str = "moving_average"  # "moving_average" or "one_euro"
    
    # Confidence validation
    confidence_stability_window: int = 5
    confidence_validation_enabled: bool = True
    
    # Performance settings
    target_fps: int = 30
    max_processing_time: float = 0.033  # ~30 FPS
    performance_monitoring: bool = True
    
    # Visual settings
    landmark_visualization: bool = True
    connection_visualization: bool = True
    confidence_overlay: bool = True
    performance_overlay: bool = True
    
    # Professional exhibition settings
    exhibition_mode: bool = True
    auto_recovery: bool = True
    error_tolerance: int = 3  # Consecutive errors before recovery
    
    # Keyboard shortcuts
    keyboard_controls: Dict[str, str] = None
    
    def __post_init__(self):
        if self.keyboard_controls is None:
            self.keyboard_controls = {
                'h': 'toggle_hand_detection',
                'b': 'toggle_pose_detection', 
                'p': 'toggle_pose_landmarks',
                'g': 'toggle_gesture_recognition',
                'r': 'reset_detection_settings',
                'escape': 'exit_application',
                'l': 'toggle_landmarks',
                'c': 'toggle_connections'
            }


@dataclass 
class DisplayConfig:
    """Configuration for display and visualization"""
    
    # Colors (BGR format for OpenCV)
    color_hand_stable: tuple = (0, 255, 0)      # Green
    color_hand_unstable: tuple = (0, 150, 255)  # Orange
    color_pose_high_conf: tuple = (0, 255, 0)   # Green
    color_pose_med_conf: tuple = (0, 255, 255)  # Yellow
    color_pose_low_conf: tuple = (0, 100, 255)  # Orange
    color_text: tuple = (255, 255, 255)         # White
    color_background: tuple = (0, 0, 0)         # Black
    
    # Text settings
    font_face: int = 0  # cv2.FONT_HERSHEY_SIMPLEX
    font_scale: float = 0.6
    font_thickness: int = 2
    
    # Landmark settings
    landmark_radius: int = 4
    landmark_thickness: int = -1  # Filled circle
    connection_thickness: int = 2
    
    # Overlay settings
    overlay_alpha: float = 0.7
    info_panel_width: int = 300
    info_panel_height: int = 150


class DetectionProfile:
    """Predefined detection profiles for different use cases"""
    
    @staticmethod
    def get_exhibition_profile() -> DetectionConfig:
        """High-performance profile for professional exhibition"""
        return DetectionConfig(
            hand_detection_enabled=True,
            pose_detection_enabled=True,
            hand_confidence_threshold=0.6,
            pose_confidence_threshold=0.6,
            smoothing_window_size=3,  # Smaller window for responsiveness
            target_fps=30,
            exhibition_mode=True,
            performance_monitoring=True
        )
    
    @staticmethod
    def get_development_profile() -> DetectionConfig:
        """Development profile with detailed debugging"""
        return DetectionConfig(
            hand_detection_enabled=True,
            pose_detection_enabled=True,
            hand_confidence_threshold=0.4,
            pose_confidence_threshold=0.4,
            smoothing_window_size=7,  # Larger window for stability
            target_fps=20,  # Lower FPS for development
            exhibition_mode=False,
            performance_monitoring=True,
            confidence_overlay=True,
            performance_overlay=True
        )
    
    @staticmethod
    def get_performance_profile() -> DetectionConfig:
        """High-performance profile optimized for speed"""
        return DetectionConfig(
            hand_detection_enabled=True,
            pose_detection_enabled=False,  # Disable pose for speed
            hand_confidence_threshold=0.7,
            smoothing_window_size=3,
            target_fps=60,
            exhibition_mode=True,
            performance_monitoring=True,
            landmark_visualization=False,  # Disable for speed
            connection_visualization=False
        )
    
    @staticmethod
    def get_accuracy_profile() -> DetectionConfig:
        """High-accuracy profile with maximum stability"""
        return DetectionConfig(
            hand_detection_enabled=True,
            pose_detection_enabled=True,
            hand_confidence_threshold=0.8,
            pose_confidence_threshold=0.8,
            smoothing_window_size=10,  # Large window for stability
            confidence_stability_window=10,
            target_fps=20,  # Lower FPS for accuracy
            exhibition_mode=False,
            performance_monitoring=True
        )


# Global detection configuration
detection_config = DetectionProfile.get_exhibition_profile()
display_config = DisplayConfig()


def update_detection_profile(profile_name: str):
    """Update global detection configuration with predefined profile"""
    global detection_config
    
    if profile_name == "exhibition":
        detection_config = DetectionProfile.get_exhibition_profile()
    elif profile_name == "development":
        detection_config = DetectionProfile.get_development_profile()
    elif profile_name == "performance":
        detection_config = DetectionProfile.get_performance_profile()
    elif profile_name == "accuracy":
        detection_config = DetectionProfile.get_accuracy_profile()
    else:
        raise ValueError(f"Unknown profile: {profile_name}")


def get_keyboard_help() -> str:
    """Get help text for keyboard shortcuts"""
    help_text = "Keyboard Controls:\n"
    help_text += "H - Toggle hand detection\n"
    help_text += "B - Toggle pose detection\n"
    help_text += "P - Toggle pose landmarks\n"
    help_text += "G - Toggle gesture recognition\n"
    help_text += "L - Toggle landmarks display\n"
    help_text += "C - Toggle connections display\n"
    help_text += "R - Reset all detection settings\n"
    help_text += "ESC - Exit application\n"
    return help_text