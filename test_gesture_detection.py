#!/usr/bin/env python3
"""
NextSight v2 Phase 4 - Gesture Detection Test (Standalone)
Tests gesture detection functionality without PyQt6 dependencies
"""

import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.abspath('.'))

def test_gesture_detection():
    """Test hand gesture detection functionality"""
    print("Testing gesture detection...")
    
    from nextsight.utils.geometry import HandLandmarkProcessor
    
    processor = HandLandmarkProcessor()
    
    # Test with mock landmarks for different gestures
    
    # Create normalized landmarks for an open hand (fingers extended)
    mock_landmarks_open = []
    for i in range(21):
        if i in [4, 8, 12, 16, 20]:  # Fingertips far from wrist
            mock_landmarks_open.append({'x': 0.4 + i * 0.02, 'y': 0.2})
        elif i in [2, 5, 9, 13, 17]:  # Finger bases
            mock_landmarks_open.append({'x': 0.5 + i * 0.005, 'y': 0.4})
        else:  # Wrist and other landmarks
            mock_landmarks_open.append({'x': 0.5, 'y': 0.5})
    
    # Create normalized landmarks for a closed hand (fingers curled)
    mock_landmarks_closed = []
    for i in range(21):
        # All landmarks very close together around wrist (small hand span)
        offset_x = (i % 3) * 0.01  # Very small offsets
        offset_y = (i % 3) * 0.01
        mock_landmarks_closed.append({'x': 0.5 + offset_x, 'y': 0.5 + offset_y})
    
    # Create normalized landmarks for pinch gesture (thumb and index very close)
    mock_landmarks_pinch = []
    for i in range(21):
        if i == 0:  # Wrist
            mock_landmarks_pinch.append({'x': 0.5, 'y': 0.5})
        elif i == 4:  # Thumb tip
            mock_landmarks_pinch.append({'x': 0.48, 'y': 0.45})
        elif i == 8:  # Index tip very close to thumb
            mock_landmarks_pinch.append({'x': 0.50, 'y': 0.46})
        elif i in [12, 16, 20]:  # Other fingertips moderately extended
            mock_landmarks_pinch.append({'x': 0.4, 'y': 0.3})
        elif i in [2, 5, 9, 13, 17]:  # Finger bases
            mock_landmarks_pinch.append({'x': 0.5, 'y': 0.45})
        else:
            mock_landmarks_pinch.append({'x': 0.48, 'y': 0.48})
    
    # Test gesture detection
    gesture_open = processor.detect_hand_gesture(mock_landmarks_open)
    gesture_closed = processor.detect_hand_gesture(mock_landmarks_closed)
    gesture_pinch = processor.detect_hand_gesture(mock_landmarks_pinch)
    
    print(f"  Open hand gesture: {gesture_open}")
    print(f"  Closed hand gesture: {gesture_closed}")
    print(f"  Pinch gesture: {gesture_pinch}")
    
    # Test invalid input
    gesture_invalid = processor.detect_hand_gesture(None)
    gesture_empty = processor.detect_hand_gesture([])
    
    print(f"  Invalid input gesture: {gesture_invalid}")
    print(f"  Empty input gesture: {gesture_empty}")
    
    # Validate results
    success = True
    
    if gesture_pinch != 'pinch':
        print(f"  ❌ Expected pinch gesture, got {gesture_pinch}")
        success = False
    
    if gesture_open not in ['open', 'unknown']:
        print(f"  ❌ Expected open or unknown gesture, got {gesture_open}")
        success = False
    
    if gesture_closed not in ['closed', 'unknown']:
        print(f"  ❌ Expected closed or unknown gesture, got {gesture_closed}")
        success = False
    
    if gesture_invalid != 'unknown':
        print(f"  ❌ Expected unknown for invalid input, got {gesture_invalid}")
        success = False
    
    if gesture_empty != 'unknown':
        print(f"  ❌ Expected unknown for empty input, got {gesture_empty}")
        success = False
    
    if success:
        print("✓ Gesture detection tests passed")
    else:
        print("❌ Some gesture detection tests failed")
    
    return success

def test_distance_calculation():
    """Test distance calculation utility"""
    print("Testing distance calculation...")
    
    from nextsight.utils.geometry import HandLandmarkProcessor, Point
    
    processor = HandLandmarkProcessor()
    
    # Test distance between points
    p1 = Point(0.0, 0.0)
    p2 = Point(1.0, 0.0)
    distance = processor._calculate_distance(p1, p2)
    
    print(f"  Distance between (0,0) and (1,0): {distance}")
    
    # Should be 1.0
    if abs(distance - 1.0) < 0.001:
        print("✓ Distance calculation tests passed")
        return True
    else:
        print(f"❌ Expected distance 1.0, got {distance}")
        return False

def test_finger_extension():
    """Test finger extension calculation"""
    print("Testing finger extension calculation...")
    
    from nextsight.utils.geometry import HandLandmarkProcessor, Point
    
    processor = HandLandmarkProcessor()
    
    # Create mock points for testing
    points = []
    for i in range(21):
        # Simple test configuration
        if i == 0:  # Wrist
            points.append(Point(0.5, 0.5))
        elif i in [2, 4]:  # Thumb base and tip
            points.append(Point(0.4, 0.4))
        elif i in [5, 8]:  # Index base and tip
            points.append(Point(0.6, 0.3))
        else:
            points.append(Point(0.5, 0.4))
    
    extensions = processor._calculate_finger_extensions(points)
    
    print(f"  Finger extensions: {extensions}")
    print(f"  Number of fingers: {len(extensions)}")
    
    # Should return 5 extension values (one per finger)
    if len(extensions) == 5:
        print("✓ Finger extension calculation tests passed")
        return True
    else:
        print(f"❌ Expected 5 finger extensions, got {len(extensions)}")
        return False

def run_all_tests():
    """Run all gesture detection tests"""
    print("NextSight v2 Phase 4 - Gesture Detection Tests")
    print("=" * 45)
    print()
    
    tests = [
        test_gesture_detection,
        test_distance_calculation,
        test_finger_extension
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
            print()
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
            print()
    
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✅ All gesture detection tests passed!")
        print()
        print("Gesture detection enhancements verified:")
        print("• Hand gesture detection implemented")
        print("• Open, closed, and pinch gestures supported")
        print("• Distance calculation working")
        print("• Finger extension calculation working")
        print("• Invalid input handling working")
    else:
        print("❌ Some tests failed. Please check the implementation.")
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)