#!/usr/bin/env python3
"""
Test script for NextSight v2 Phase 3 zone management system
Tests zone creation, intersection detection, and UI integration
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_zone_config():
    """Test zone configuration and data models"""
    print("Testing zone configuration...")
    
    from nextsight.zones.zone_config import Zone, ZoneType, ZoneConfig
    
    # Test zone creation
    zone = Zone(
        id="test_001",
        name="Test Pick Zone",
        zone_type=ZoneType.PICK,
        x=0.2, y=0.3, width=0.2, height=0.15
    )
    
    assert zone.zone_type == ZoneType.PICK
    assert zone.contains_point(0.25, 0.35)
    assert not zone.contains_point(0.1, 0.1)
    
    # Test zone config
    config = ZoneConfig("/tmp/test_zones.json")
    assert config.add_zone(zone)
    assert len(config.zones) == 1
    
    retrieved = config.get_zone("test_001")
    assert retrieved is not None
    assert retrieved.name == "Test Pick Zone"
    
    print("✓ Zone configuration tests passed")


def test_geometry_utils():
    """Test geometric utility functions"""
    print("Testing geometry utilities...")
    
    from nextsight.utils.geometry import (
        Point, Rectangle, HandLandmarkProcessor,
        ZoneIntersectionCalculator, normalize_coordinates
    )
    
    # Test point and rectangle
    point = Point(0.5, 0.5)
    rect = Rectangle(0.2, 0.2, 0.6, 0.6)
    
    assert rect.contains_point(point)
    assert rect.area() == 0.36
    
    # Test coordinate normalization
    norm_x, norm_y = normalize_coordinates(320, 240, 640, 480)
    assert norm_x == 0.5
    assert norm_y == 0.5
    
    print("✓ Geometry utility tests passed")


def test_intersection_detection():
    """Test hand-zone intersection detection"""
    print("Testing intersection detection...")
    
    from nextsight.zones.intersection_detector import IntersectionDetector
    from nextsight.zones.zone_config import Zone, ZoneType
    
    detector = IntersectionDetector()
    
    # Create test zone
    zone = Zone(
        id="test_zone",
        name="Test Zone",
        zone_type=ZoneType.PICK,
        x=0.2, y=0.2, width=0.4, height=0.4
    )
    
    # Test with empty detection info
    result = detector.detect_intersections([zone], {'hands': {}})
    assert 'intersections' in result
    assert 'events' in result
    assert 'statistics' in result
    
    print("✓ Intersection detection tests passed")


def test_zone_manager():
    """Test zone manager functionality"""
    print("Testing zone manager...")
    
    from nextsight.zones.zone_manager import ZoneManager
    from nextsight.zones.zone_config import ZoneType
    
    manager = ZoneManager("/tmp/test_zone_manager.json")
    
    # Test zone creation
    zone = manager.create_zone_direct(
        "Test Zone", ZoneType.PICK,
        0.1, 0.1, 0.3, 0.3
    )
    
    assert zone is not None
    assert len(manager.get_zones()) == 1
    
    # Test zone deletion
    success = manager.delete_zone(zone.id)
    assert success
    assert len(manager.get_zones()) == 0
    
    print("✓ Zone manager tests passed")


def test_ui_components():
    """Test UI component creation (without display)"""
    print("Testing UI components...")
    
    try:
        # Test imports
        from nextsight.ui.zone_overlay import ZoneOverlay
        from nextsight.ui.context_menu import ZoneContextMenu
        from nextsight.zones.zone_creator import ZoneCreator
        
        # Test object creation (without showing UI)
        creator = ZoneCreator()
        assert creator is not None
        
        status = creator.get_creation_status()
        assert 'is_creating' in status
        assert not status['is_creating']
        
        print("✓ UI component tests passed")
        
    except ImportError as e:
        print(f"⚠ UI components require PyQt6 (skipped): {e}")


def run_all_tests():
    """Run all zone system tests"""
    print("NextSight v2 Phase 3 - Zone Management System Tests")
    print("=" * 55)
    print()
    
    try:
        test_zone_config()
        test_geometry_utils() 
        test_intersection_detection()
        test_zone_manager()
        test_ui_components()
        
        print()
        print("✅ All tests passed! Zone management system is ready.")
        print()
        print("To run the demo:")
        print("python demo_phase3.py")
        return 0
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())