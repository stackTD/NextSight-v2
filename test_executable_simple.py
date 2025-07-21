#!/usr/bin/env python3
"""
Simple test script to be executed by the built PyInstaller executable.
Tests MediaPipe imports within the standalone executable.
"""

import sys

try:
    # Test the imports that were failing
    import matplotlib
    import mediapipe
    from nextsight.vision.hand_tracker import HandTracker
    
    print("SUCCESS: All MediaPipe dependencies work in the executable!")
    print(f"matplotlib version: {matplotlib.__version__}")
    print(f"mediapipe version: {mediapipe.__version__}")
    print("HandTracker can be imported and used.")
    
    # Quick test of HandTracker initialization
    tracker = HandTracker()
    print("HandTracker initialized successfully in executable.")
    
except ImportError as e:
    print(f"FAILED: Import error in executable: {e}")
    sys.exit(1)
except Exception as e:
    print(f"FAILED: Error in executable: {e}")
    sys.exit(1)