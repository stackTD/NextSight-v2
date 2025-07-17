#!/usr/bin/env python3
"""
NextSight v2 - Professional Computer Vision Exhibition Demo
Main entry point for the application
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from nextsight.core.application import create_application


def main():
    """Main entry point"""
    try:
        # Create and run application
        app = create_application()
        return app.run()
        
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        return 0
    except Exception as e:
        print(f"Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())