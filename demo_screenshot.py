#!/usr/bin/env python3
"""
Visual demonstration script for NextSight v2
Creates a screenshot of the application in action
"""

import sys
import os
import time

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer, QRect
from PyQt6.QtGui import QPixmap, QImage, QPainter, QColor, QFont, QPen
from nextsight.core.application import create_application
import numpy as np
import cv2


def create_demo_frame():
    """Create a demo frame with simulated hand detection"""
    # Create a demo image with some visual content
    frame = np.zeros((720, 1280, 3), dtype=np.uint8)
    
    # Add gradient background
    for y in range(720):
        intensity = int(30 + (y / 720) * 50)
        frame[y, :] = [intensity//3, intensity//2, intensity]
    
    # Add some demo text
    cv2.putText(frame, "NextSight v2 - Exhibition Demo", (50, 100), 
                cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
    
    cv2.putText(frame, "Professional Computer Vision Platform", (50, 150), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (200, 200, 200), 2)
    
    # Add demo hand landmarks (simulated)
    # Hand 1 - Right hand
    hand1_points = [
        (400, 300), (420, 280), (440, 260), (460, 240), (480, 220),  # Thumb
        (380, 250), (360, 230), (340, 210), (320, 200),  # Index finger
        (380, 280), (360, 260), (340, 240), (320, 230),  # Middle finger
        (380, 310), (370, 290), (360, 270), (350, 260),  # Ring finger
        (380, 340), (375, 320), (370, 300), (365, 290),  # Pinky
    ]
    
    # Draw hand landmarks
    for i, point in enumerate(hand1_points):
        color = (0, 255, 0) if i < 5 else (255, 0, 255)  # Different colors for different fingers
        cv2.circle(frame, point, 8, color, -1)
        cv2.circle(frame, point, 8, (255, 255, 255), 2)
    
    # Draw connections
    connections = [
        [(0, 1), (1, 2), (2, 3), (3, 4)],  # Thumb
        [(5, 6), (6, 7), (7, 8)],  # Index
        [(9, 10), (10, 11), (11, 12)],  # Middle
        [(13, 14), (14, 15), (15, 16)],  # Ring
        [(17, 18), (18, 19), (19, 20)],  # Pinky
    ]
    
    for finger_connections in connections:
        for start_idx, end_idx in finger_connections:
            if start_idx < len(hand1_points) and end_idx < len(hand1_points):
                cv2.line(frame, hand1_points[start_idx], hand1_points[end_idx], (0, 255, 255), 2)
    
    # Add hand label
    cv2.rectangle(frame, (350, 370), (450, 400), (0, 0, 0), -1)
    cv2.putText(frame, "Right", (365, 390), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    
    # Add performance indicators
    cv2.putText(frame, "FPS: 30.5", (50, 680), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.putText(frame, "Hands: 1", (200, 680), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
    
    return frame


def main():
    """Create visual demonstration"""
    print("Creating NextSight v2 visual demonstration...")
    
    # Set environment for headless operation
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    
    try:
        # Create application
        app = create_application()
        main_window = app.main_window
        
        # Show the main window (offscreen)
        main_window.show()
        
        # Create demo frame
        demo_frame = create_demo_frame()
        
        # Convert to QImage
        height, width, channel = demo_frame.shape
        bytes_per_line = 3 * width
        rgb_image = cv2.cvtColor(demo_frame, cv2.COLOR_BGR2RGB)
        qt_image = QImage(rgb_image.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        
        # Update the camera widget with demo frame
        detection_info = {
            'hands_detected': 1,
            'hand_landmarks': [[]],  # Simplified for demo
            'handedness': ['Right']
        }
        
        camera_widget = main_window.get_main_widget().get_camera_widget()
        camera_widget.update_frame(qt_image, detection_info)
        camera_widget.update_fps(30.5)
        
        # Update status bar
        status_bar = main_window.get_status_bar()
        status_bar.set_camera_status(True)
        status_bar.set_detection_status(True)
        status_bar.update_fps(30.5)
        status_bar.update_hands_count(1)
        
        # Update main widget
        main_widget = main_window.get_main_widget()
        main_widget.update_fps_display(30.5)
        main_widget.update_detection_info(detection_info)
        
        # Process events to update UI
        QApplication.processEvents()
        
        # Take screenshot
        screenshot = main_window.grab()
        screenshot_path = "nextsight_v2_demo_screenshot.png"
        screenshot.save(screenshot_path)
        
        print(f"✓ Screenshot saved as: {screenshot_path}")
        print(f"✓ Window size: {main_window.size().width()}x{main_window.size().height()}")
        print(f"✓ Application features demonstrated:")
        print("  - Professional dark theme UI")
        print("  - Custom title bar with NextSight branding")
        print("  - Real-time camera display with hand detection overlay")
        print("  - Control panel with detection settings")
        print("  - Comprehensive status bar with performance metrics")
        print("  - Hand landmark visualization with connections")
        
        return True
        
    except Exception as e:
        print(f"✗ Demo creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)