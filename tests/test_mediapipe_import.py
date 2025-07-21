#!/usr/bin/env python3
"""
Test MediaPipe imports to verify PyInstaller build includes all dependencies.
This test reproduces the MediaPipe/matplotlib import issue.
"""

import sys
import traceback

def test_mediapipe_imports():
    """Test all MediaPipe-related imports that NextSight uses"""
    print("Testing MediaPipe imports...")
    
    # Test basic imports
    try:
        import mediapipe as mp
        print("✓ mediapipe imported successfully")
        print(f"  MediaPipe version: {mp.__version__}")
    except ImportError as e:
        print(f"✗ Failed to import mediapipe: {e}")
        return False
    
    # Test MediaPipe solutions
    try:
        from mediapipe.python.solutions import hands
        print("✓ mediapipe.python.solutions.hands imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import mediapipe hands: {e}")
        return False
    
    # Test drawing utilities
    try:
        from mediapipe.python.solutions import drawing_utils
        print("✓ mediapipe.python.solutions.drawing_utils imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import mediapipe drawing_utils: {e}")
        return False
    
    # Test drawing styles
    try:
        from mediapipe.python.solutions import drawing_styles
        print("✓ mediapipe.python.solutions.drawing_styles imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import mediapipe drawing_styles: {e}")
        return False
    
    # Test matplotlib (required by MediaPipe)
    try:
        import matplotlib
        print("✓ matplotlib imported successfully")
        print(f"  Matplotlib version: {matplotlib.__version__}")
    except ImportError as e:
        print(f"✗ Failed to import matplotlib: {e}")
        print("  This is the issue described in the problem statement!")
        return False
    
    # Test other MediaPipe dependencies
    dependencies = [
        ('numpy', 'numpy'), 
        ('cv2', 'cv2'), 
        ('google.protobuf', 'protobuf'), 
        ('attrs', 'attrs'), 
        ('absl', 'absl'), 
        ('flatbuffers', 'flatbuffers')
    ]
    
    for import_name, display_name in dependencies:
        try:
            if import_name == 'cv2':
                import cv2
                print(f"✓ {display_name} imported successfully (version: {cv2.__version__})")
            elif import_name == 'absl':
                import absl
                print(f"✓ {display_name} imported successfully")
            elif import_name == 'google.protobuf':
                import google.protobuf
                print(f"✓ {display_name} imported successfully (version: {google.protobuf.__version__})")
            else:
                module = __import__(import_name)
                version = getattr(module, '__version__', 'unknown')
                print(f"✓ {display_name} imported successfully (version: {version})")
        except ImportError as e:
            print(f"✗ Failed to import {display_name}: {e}")
            return False
    
    # Test MediaPipe hands initialization (this is what NextSight actually uses)
    try:
        hands_solution = mp.solutions.hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        print("✓ MediaPipe Hands solution initialized successfully")
        hands_solution.close()
    except Exception as e:
        print(f"✗ Failed to initialize MediaPipe Hands: {e}")
        traceback.print_exc()
        return False
    
    print("\n✓ All MediaPipe imports successful!")
    return True

if __name__ == "__main__":
    success = test_mediapipe_imports()
    sys.exit(0 if success else 1)