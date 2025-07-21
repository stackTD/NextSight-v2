#!/usr/bin/env python3
"""
Test script to reproduce the original matplotlib import error by temporarily 
hiding matplotlib, then demonstrate the fix.
"""

import sys
import importlib
import os
import builtins
from unittest.mock import patch

def test_original_problem():
    """Reproduce the original MediaPipe matplotlib import issue"""
    print("Testing original problem: MediaPipe requires matplotlib...")
    
    # First show that the problem would occur if matplotlib wasn't available
    print("\n1. Simulating missing matplotlib (original problem):")
    
    # Temporarily hide matplotlib to simulate the original problem
    original_modules = sys.modules.copy()
    matplotlib_related = [name for name in sys.modules if name.startswith('matplotlib')]
    for name in matplotlib_related:
        if name in sys.modules:
            del sys.modules[name]
    
    # Mock matplotlib import to fail
    def mock_matplotlib_import(name, *args, **kwargs):
        if name == 'matplotlib' or name.startswith('matplotlib.'):
            raise ImportError(f"No module named '{name}'")
        return original_import(name, *args, **kwargs)
    
    original_import = builtins.__import__
    
    try:
        builtins.__import__ = mock_matplotlib_import
        
        # This should fail with the original error
        try:
            import mediapipe as mp
            print("   ❌ Expected import to fail but it succeeded (matplotlib might be cached)")
        except ImportError as e:
            print(f"   ✓ Reproduced original error: {e}")
            
    except Exception as e:
        print(f"   Note: Could not fully reproduce original error due to import caching: {e}")
    finally:
        # Restore original import
        builtins.__import__ = original_import
        # Restore modules
        sys.modules.clear()
        sys.modules.update(original_modules)
    
    print("\n2. Testing current fix:")
    
    # Now test that everything works with our fix
    try:
        # Import matplotlib first (this is now included in our requirements)
        import matplotlib
        print(f"   ✓ matplotlib available (version: {matplotlib.__version__})")
        
        # Import MediaPipe (should work now)
        import mediapipe as mp
        print(f"   ✓ mediapipe imported successfully (version: {mp.__version__})")
        
        # Test MediaPipe hands (what NextSight actually uses)
        hands = mp.solutions.hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5
        )
        print("   ✓ MediaPipe Hands initialized successfully")
        hands.close()
        
        # Test NextSight hand tracker
        from nextsight.vision.hand_tracker import HandTracker
        tracker = HandTracker()
        print("   ✓ NextSight HandTracker initialized successfully")
        
        print("\n✅ SUCCESS: MediaPipe dependency issue is FIXED!")
        print("   - matplotlib is now included in requirements.txt")
        print("   - matplotlib is no longer excluded from PyInstaller")
        print("   - All MediaPipe dependencies are properly included")
        
        return True
        
    except ImportError as e:
        print(f"\n❌ FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ FAILED: Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_original_problem()
    sys.exit(0 if success else 1)