"""
Configuration settings for NextSight v2
"""

import os
from dataclasses import dataclass
from typing import Tuple


@dataclass
class CameraConfig:
    """Camera configuration settings"""
    default_index: int = 0
    width: int = 1280
    height: int = 720
    fps: int = 30
    
    
@dataclass
class HandDetectionConfig:
    """Hand detection configuration settings"""
    confidence_threshold: float = 0.5
    tracking_confidence: float = 0.5
    max_num_hands: int = 2
    model_complexity: int = 1
    

@dataclass
class UIConfig:
    """UI configuration settings"""
    window_title: str = "NextSight v2 - Exhibition Demo"
    window_width: int = 1400
    window_height: int = 900
    min_width: int = 1000
    min_height: int = 600
    

@dataclass
class AppConfig:
    """Main application configuration"""
    camera: CameraConfig = CameraConfig()
    hand_detection: HandDetectionConfig = HandDetectionConfig()
    ui: UIConfig = UIConfig()
    
    # Performance settings
    target_fps: int = 30
    enable_performance_stats: bool = True
    
    # Logging
    log_level: str = "INFO"
    
    
# Global configuration instance
config = AppConfig()