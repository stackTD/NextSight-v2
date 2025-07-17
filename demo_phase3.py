#!/usr/bin/env python3
"""
NextSight v2 Phase 3 - Zone Management & Hand-Zone Interaction Demo
Demonstrates the complete zone management system with pick/drop functionality
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from nextsight.core.application import create_application


def main():
    """Run the NextSight v2 Phase 3 demo"""
    print("NextSight v2 - Phase 3: Zone Management & Hand-Zone Interaction Demo")
    print("=" * 65)
    print()
    print("KEYBOARD CONTROLS:")
    print("=" * 20)
    print("DETECTION CONTROLS:")
    print("H - Toggle hand detection")
    print("B - Toggle pose detection")
    print("P - Toggle pose landmarks")
    print("G - Toggle gesture recognition")
    print("L - Toggle landmarks display")
    print("C - Toggle connections display")
    print("R - Reset all detection settings")
    print()
    print("ZONE CONTROLS:")
    print("Z - Toggle zone system on/off")
    print("1 - Create pick zone (then click & drag)")
    print("2 - Create drop zone (then click & drag)")
    print("Delete - Clear all zones")
    print("Right-click - Zone context menu")
    print()
    print("SYSTEM:")
    print("F1 - Show help dialog")
    print("ESC - Exit application")
    print()
    print("MOUSE INTERACTION:")
    print("=" * 20)
    print("• Left-click & drag - Create zones when in creation mode")
    print("• Right-click - Open context menu")
    print("• Right-click on zone - Zone-specific menu")
    print("• Hover over zones - Highlight zones")
    print()
    print("FEATURES:")
    print("=" * 10)
    print("• Interactive zone creation with mouse")
    print("• Real-time hand-zone intersection detection")
    print("• Color-coded zones (Pick=Green, Drop=Blue)")
    print("• Professional zone visualization with labels")
    print("• Live pick/drop event tracking in status bar")
    print("• Zone persistence (save/load configurations)")
    print("• Context menu for zone management")
    print("• Multi-hand zone interaction support")
    print("• Exhibition-ready professional interface")
    print()
    print("DEMO INSTRUCTIONS:")
    print("=" * 18)
    print("1. Press 'Z' to enable the zone system")
    print("2. Press '1' to create a pick zone, then click & drag")
    print("3. Press '2' to create a drop zone, then click & drag")
    print("4. Move your hands into the zones to see detection")
    print("5. Watch the status bar for pick/drop events")
    print("6. Right-click for zone management options")
    print()
    print("Starting application...")
    print("=" * 65)
    
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