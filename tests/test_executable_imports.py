#!/usr/bin/env python3
"""
Test built executable for MediaPipe imports.
This script will be used to test the executable in a controlled way.
"""

import sys
import traceback

def main():
    """Test MediaPipe imports that caused the original issue"""
    print("Testing MediaPipe imports in built executable...")
    
    try:
        # Test the import chain that was failing:
        # main.py → nextsight.core.application → nextsight.core.camera_thread → 
        # nextsight.vision.detector → nextsight.vision.hand_tracker → mediapipe → matplotlib
        
        print("Testing import chain that was failing...")
        
        # Test matplotlib first (this was the failing import)
        import matplotlib
        print(f"✓ matplotlib imported successfully (version: {matplotlib.__version__})")
        
        # Test MediaPipe
        import mediapipe as mp
        print(f"✓ mediapipe imported successfully (version: {mp.__version__})")
        
        # Test MediaPipe solutions that NextSight uses
        from mediapipe.python.solutions import hands
        print("✓ mediapipe.python.solutions.hands imported successfully")
        
        from mediapipe.python.solutions import drawing_utils
        print("✓ mediapipe.python.solutions.drawing_utils imported successfully")
        
        # Test MediaPipe hands initialization
        hands_solution = mp.solutions.hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        print("✓ MediaPipe Hands solution initialized successfully")
        hands_solution.close()
        
        # Test the actual NextSight hand tracker
        from nextsight.vision.hand_tracker import HandTracker
        print("✓ NextSight HandTracker imported successfully")
        
        tracker = HandTracker()
        print("✓ NextSight HandTracker initialized successfully")
        
        print("\n✅ SUCCESS: All MediaPipe imports work in the built executable!")
        print("The ModuleNotFoundError: No module named 'matplotlib' has been fixed!")
        return 0
        
    except ImportError as e:
        print(f"\n❌ FAILED: Import error occurred: {e}")
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n❌ FAILED: Unexpected error: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())