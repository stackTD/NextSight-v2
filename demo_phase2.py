#!/usr/bin/env python3
"""
NextSight v2 Phase 2 - Live Demo Script
Demonstrates enhanced detection engine with keyboard controls
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from nextsight.core.application import create_application


def main():
    """Run the NextSight v2 Phase 2 demo"""
    print("NextSight v2 - Phase 2 Detection Engine Demo")
    print("=" * 50)
    print()
    print("KEYBOARD CONTROLS:")
    print("H - Toggle hand detection")
    print("B - Toggle pose detection")
    print("P - Toggle pose landmarks")
    print("G - Toggle gesture recognition")
    print("L - Toggle landmarks display")
    print("C - Toggle connections display")
    print("R - Reset all detection settings")
    print("F1 - Show help dialog")
    print("ESC - Exit application")
    print()
    print("FEATURES:")
    print("• Enhanced hand tracking with smoothing")
    print("• MediaPipe pose detection for upper body")
    print("• Professional keyboard controls")
    print("• Multi-modal detection coordination")
    print("• Real-time performance monitoring")
    print("• Exhibition-ready stability")
    print()
    print("Starting application...")
    print("=" * 50)
    
    try:
        # Create and run application
        app = create_application()
        return app.run()
        
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())