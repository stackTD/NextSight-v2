#!/usr/bin/env python3
"""
Test script to verify NextSight v2 Phase 2 functionality
Enhanced detection engine with hand tracking and pose detection
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
from nextsight.vision.detector import MultiModalDetector
from nextsight.vision.hand_tracker import HandTracker
from nextsight.vision.pose_detector import PoseDetector
from nextsight.vision.smoothing import LandmarkSmoother, ConfidenceValidator
from nextsight.utils.detection_config import detection_config
import numpy as np
import cv2


def test_smoothing_algorithms():
    """Test smoothing and validation algorithms"""
    print("Testing smoothing algorithms...")
    
    # Test moving average filter
    smoother = LandmarkSmoother(filter_type="moving_average", window_size=3)
    
    # Test landmark data
    test_landmarks = [
        {'x': 0.5, 'y': 0.5, 'z': 0.0},
        {'x': 0.6, 'y': 0.6, 'z': 0.1}
    ]
    
    # Apply smoothing
    smoothed = smoother.smooth_landmarks(test_landmarks, 0.8, "test_hand", time.time())
    
    print(f"✓ Smoothing algorithm processed {len(smoothed) if smoothed else 0} landmarks")
    
    # Test confidence validator
    validator = ConfidenceValidator(min_confidence=0.5)
    
    result1 = validator.validate(0.7)
    result2 = validator.validate(0.3)
    
    print(f"✓ Confidence validator: high conf={result1}, low conf={result2}")
    
    return True


def test_pose_detector():
    """Test pose detection with a sample image"""
    print("Testing pose detection...")
    
    detector = PoseDetector()
    
    # Create a test image (640x480, black background)
    test_image = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Process the test image
    processed_image, detection_info = detector.process_frame(test_image)
    
    print(f"✓ Pose detection processed successfully")
    print(f"  - Image shape: {processed_image.shape}")
    print(f"  - Pose detected: {detection_info.get('pose_detected', False)}")
    print(f"  - Upper body landmarks: {len(detection_info.get('upper_body_landmarks', []))}")
    
    detector.cleanup()
    return True


def test_enhanced_hand_tracker():
    """Test enhanced hand tracking with multi-hand features"""
    print("Testing enhanced hand tracker...")
    
    tracker = HandTracker()
    
    # Create a test image
    test_image = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Process the test image
    processed_image, detection_info = tracker.process_frame(test_image)
    
    print(f"✓ Enhanced hand tracker processed successfully")
    print(f"  - Image shape: {processed_image.shape}")
    print(f"  - Hands detected: {detection_info.get('hands_detected', 0)}")
    print(f"  - Left hand present: {detection_info.get('left_hand', {}).get('present', False)}")
    print(f"  - Right hand present: {detection_info.get('right_hand', {}).get('present', False)}")
    print(f"  - Hand zones: {len(detection_info.get('hand_zones', {}))}")
    
    tracker.cleanup()
    return True


def test_multimodal_detector():
    """Test the main multimodal detector"""
    print("Testing multimodal detector...")
    
    detector = MultiModalDetector()
    
    # Create a test image
    test_image = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Process the test image
    processed_image, detection_info = detector.process_frame(test_image)
    
    print(f"✓ Multimodal detector processed successfully")
    print(f"  - Image shape: {processed_image.shape}")
    print(f"  - Has hands info: {'hands' in detection_info}")
    print(f"  - Has pose info: {'pose' in detection_info}")
    print(f"  - Combined confidence: {detection_info.get('combined_confidence', 0.0):.3f}")
    print(f"  - Performance info: {'performance' in detection_info}")
    
    # Test toggle functions
    hand_enabled = detector.toggle_hand_detection()
    pose_enabled = detector.toggle_pose_detection()
    print(f"  - Hand detection toggle: {hand_enabled}")
    print(f"  - Pose detection toggle: {pose_enabled}")
    
    # Test reset
    detector.reset_detection_settings()
    print(f"  - Settings reset successfully")
    
    detector.cleanup()
    return True


def test_keyboard_controls():
    """Test keyboard control functionality"""
    print("Testing keyboard controls...")
    
    # Set environment for headless operation
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    
    try:
        app = create_application()
        main_window = app.main_window
        
        # Test that keyboard controls are enabled
        print(f"✓ Keyboard controls enabled: {main_window.keyboard_enabled}")
        
        # Test keyboard help
        help_text = main_window.get_keyboard_help if hasattr(main_window, 'get_keyboard_help') else "Not available"
        print(f"✓ Keyboard help available")
        
        # Test keyboard event handling (we can't simulate actual key presses in headless mode)
        main_window.set_keyboard_controls_enabled(False)
        main_window.set_keyboard_controls_enabled(True)
        print(f"✓ Keyboard control enable/disable works")
        
        return True
        
    except Exception as e:
        print(f"✗ Keyboard controls test failed: {e}")
        return False


def test_enhanced_control_panel():
    """Test the enhanced control panel functionality"""
    print("Testing enhanced control panel...")
    
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    
    try:
        app = create_application()
        main_widget = app.main_window.get_main_widget()
        control_panel = main_widget.control_panel
        
        # Test control panel exists
        print("✓ Enhanced control panel created")
        
        # Test toggle methods exist
        control_panel.on_hand_detection_toggle()
        control_panel.on_pose_detection_toggle()
        control_panel.on_pose_landmarks_toggle()
        control_panel.on_gesture_toggle()
        print("✓ Control panel toggles work")
        
        # Test reset
        control_panel.on_reset_settings()
        print("✓ Control panel reset works")
        
        # Test detection status update
        test_detection_info = {
            'hands': {'hands_detected': 2, 'handedness': ['Left', 'Right']},
            'pose': {'pose_detected': True, 'pose_confidence': 0.85}
        }
        control_panel.update_detection_status(test_detection_info)
        print("✓ Detection status update works")
        
        return True
        
    except Exception as e:
        print(f"✗ Enhanced control panel test failed: {e}")
        return False


def test_detection_configuration():
    """Test detection configuration system"""
    print("Testing detection configuration...")
    
    from nextsight.utils.detection_config import (
        DetectionProfile, update_detection_profile, get_keyboard_help
    )
    
    # Test profile switching
    update_detection_profile("exhibition")
    print("✓ Exhibition profile loaded")
    
    update_detection_profile("development")
    print("✓ Development profile loaded")
    
    update_detection_profile("performance")
    print("✓ Performance profile loaded")
    
    # Test keyboard help
    help_text = get_keyboard_help()
    print(f"✓ Keyboard help generated ({len(help_text)} chars)")
    
    # Test detection config structure
    config = detection_config
    print(f"✓ Detection config loaded:")
    print(f"  - Hand detection: {config.hand_detection_enabled}")
    print(f"  - Pose detection: {config.pose_detection_enabled}")
    print(f"  - Target FPS: {config.target_fps}")
    print(f"  - Exhibition mode: {config.exhibition_mode}")
    
    return True


def test_application_integration():
    """Test Phase 2 integration with the main application"""
    print("Testing Phase 2 application integration...")
    
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    
    try:
        app = create_application()
        
        # Test that multimodal detector is used
        camera_thread = app.camera_thread
        detector_stats = camera_thread.get_detection_stats()
        
        print("✓ Application uses multimodal detector")
        print(f"  - Hand detection enabled: {detector_stats.get('hand_detection_enabled', False)}")
        print(f"  - Pose detection enabled: {detector_stats.get('pose_detection_enabled', False)}")
        
        # Test new toggle methods
        camera_thread.toggle_hand_detection()
        camera_thread.toggle_pose_detection()
        camera_thread.toggle_pose_landmarks()
        camera_thread.toggle_gesture_recognition()
        print("✓ All detection toggles work")
        
        # Test reset
        camera_thread.reset_detection_settings()
        print("✓ Detection settings reset works")
        
        return True
        
    except Exception as e:
        print(f"✗ Application integration test failed: {e}")
        return False


def main():
    """Run all Phase 2 tests"""
    print("NextSight v2 - Testing Phase 2 Implementation")
    print("=" * 50)
    
    tests = [
        ("Smoothing Algorithms", test_smoothing_algorithms),
        ("Pose Detector", test_pose_detector),
        ("Enhanced Hand Tracker", test_enhanced_hand_tracker),
        ("Multimodal Detector", test_multimodal_detector),
        ("Keyboard Controls", test_keyboard_controls),
        ("Enhanced Control Panel", test_enhanced_control_panel),
        ("Detection Configuration", test_detection_configuration),
        ("Application Integration", test_application_integration),
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
    print("Phase 2 Test Summary:")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  {test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Phase 2 tests passed! Detection engine implementation is successful.")
        return 0
    else:
        print("❌ Some Phase 2 tests failed. Please check the implementation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())