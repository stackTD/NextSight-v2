#!/usr/bin/env python3
"""
Test script to verify NextSight v2 basic functionality
"""

import sys
import os
import time

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from nextsight.core.application import create_application
from nextsight.vision.detector import HandDetector
import numpy as np
import cv2


def test_hand_detector():
    """Test MediaPipe hand detection with a sample image"""
    print("Testing MediaPipe hand detection...")
    
    detector = HandDetector()
    
    # Create a test image (640x480, black background)
    test_image = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Process the test image
    processed_image, detection_info = detector.process_frame(test_image)
    
    print(f"✓ Hand detection processed successfully")
    print(f"  - Image shape: {processed_image.shape}")
    print(f"  - Detection info: {detection_info}")
    
    detector.cleanup()
    return True


def test_application_creation():
    """Test application creation and basic setup"""
    print("Testing application creation...")
    
    # Set environment for headless operation
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    
    try:
        app = create_application()
        print("✓ Application created successfully")
        
        main_window = app.main_window
        print("✓ Main window created")
        
        camera_widget = main_window.get_main_widget().get_camera_widget()
        print("✓ Camera widget accessible")
        
        status_bar = main_window.get_status_bar()
        print("✓ Status bar accessible")
        
        # Test configuration
        from nextsight.utils.config import config
        print(f"✓ Configuration loaded: {config.ui.window_title}")
        
        return True
        
    except Exception as e:
        print(f"✗ Application creation failed: {e}")
        return False


def test_ui_functionality():
    """Test UI component functionality"""
    print("Testing UI functionality...")
    
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    
    try:
        app = create_application()
        main_widget = app.main_window.get_main_widget()
        
        # Test control panel functionality
        main_widget.on_detection_toggle()
        print("✓ Detection toggle works")
        
        main_widget.on_confidence_changed(75)
        print("✓ Confidence threshold adjustment works")
        
        # Test camera widget
        camera_widget = main_widget.get_camera_widget()
        camera_widget.toggle_info_overlay()
        print("✓ Info overlay toggle works")
        
        # Test status bar
        status_bar = app.main_window.get_status_bar()
        status_bar.set_camera_status(True)
        status_bar.set_detection_status(True)
        status_bar.update_fps(30.0)
        status_bar.update_hands_count(2)
        print("✓ Status bar updates work")
        
        return True
        
    except Exception as e:
        print(f"✗ UI functionality test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("NextSight v2 - Testing Phase 1 Implementation")
    print("=" * 50)
    
    tests = [
        ("MediaPipe Hand Detection", test_hand_detector),
        ("Application Creation", test_application_creation), 
        ("UI Functionality", test_ui_functionality),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * len(test_name))
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                print(f"✓ {test_name} passed")
            else:
                print(f"✗ {test_name} failed")
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary:")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  {test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Phase 1 implementation is successful.")
        return 0
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())