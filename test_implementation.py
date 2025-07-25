#!/usr/bin/env python3
"""
Manual verification test for NextSight v2 zone editing and process management features
This script tests the core functionality without requiring a GUI display
"""

import sys
import os
import tempfile
import json

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Test imports
try:
    from nextsight.core.process_manager import ProcessManager, Process
    from nextsight.zones.zone_config import Zone, ZoneType, ZoneConfig
    from nextsight.zones.zone_manager import ZoneManager
    from nextsight.ui.zone_editor import ZoneEditor, ControlPoint
    print("✓ All imports successful")
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)


def test_process_persistence():
    """Test process persistence and numbering consistency"""
    print("\n=== Testing Process Persistence ===")
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        # Create first process manager
        pm1 = ProcessManager(temp_file)
        
        # Create some processes
        p1 = pm1.create_process("Test Process 1")
        p2 = pm1.create_process("Test Process 2")
        p3 = pm1.create_process("Test Process 3")
        
        assert p1.id == "process_1", f"Expected process_1, got {p1.id}"
        assert p2.id == "process_2", f"Expected process_2, got {p2.id}"
        assert p3.id == "process_3", f"Expected process_3, got {p3.id}"
        print("✓ Process numbering consistency verified")
        
        # Delete middle process
        pm1.delete_process("process_2")
        
        # Create new process manager (simulating restart)
        pm2 = ProcessManager(temp_file)
        
        # Process counter should be updated correctly
        p4 = pm2.create_process("Test Process 4")
        assert p4.id == "process_4", f"Expected process_4, got {p4.id}"
        print("✓ Process counter persistence verified")
        
        # Verify existing processes are loaded
        assert pm2.get_process("process_1") is not None, "Process 1 should exist"
        assert pm2.get_process("process_2") is None, "Process 2 should be deleted"
        assert pm2.get_process("process_3") is not None, "Process 3 should exist"
        print("✓ Process loading verification passed")
        
    finally:
        os.unlink(temp_file)
    
    print("✓ Process persistence tests passed")


def test_zone_creation_and_editing():
    """Test zone creation and editing functionality"""
    print("\n=== Testing Zone Creation and Editing ===")
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        # Create zone manager
        zm = ZoneManager(temp_file)
        
        # Test zone creation
        zone1 = zm.create_zone_direct("Pick Zone 1", ZoneType.PICK, 0.1, 0.1, 0.3, 0.3)
        zone2 = zm.create_zone_direct("Drop Zone 1", ZoneType.DROP, 0.6, 0.6, 0.3, 0.3)
        
        assert zone1 is not None, "Zone 1 creation failed"
        assert zone2 is not None, "Zone 2 creation failed"
        print("✓ Zone creation verified")
        
        # Test zone modification (simulating editor)
        original_width = zone1.width
        zone1.width = 0.4  # Resize zone
        success = zm.update_zone(zone1)
        assert success, "Zone update failed"
        assert zone1.width == 0.4, f"Expected width 0.4, got {zone1.width}"
        print("✓ Zone modification verified")
        
        # Test zone persistence
        zm.save_configuration()
        
        # Create new zone manager (simulating restart)
        zm2 = ZoneManager(temp_file)
        zm2.load_configuration()
        
        loaded_zone1 = zm2.get_zone(zone1.id)
        assert loaded_zone1 is not None, "Zone not loaded"
        assert loaded_zone1.width == 0.4, f"Zone width not persisted correctly"
        print("✓ Zone persistence verified")
        
    finally:
        os.unlink(temp_file)
    
    print("✓ Zone creation and editing tests passed")


def test_control_point_creation():
    """Test zone editor control point creation"""
    print("\n=== Testing Zone Editor Control Points ===")
    
    # Create a test zone
    zone = Zone(
        id="test_zone",
        name="Test Zone",
        zone_type=ZoneType.PICK,
        x=0.2, y=0.2, width=0.4, height=0.3,
        color="#00ff00"
    )
    
    # Simulate control point creation (without GUI)
    x1, y1 = zone.x, zone.y
    x2, y2 = zone.x + zone.width, zone.y + zone.height
    
    # Corner control points
    corner_points = [
        ControlPoint(x1, y1, 'corner_tl', zone.id),  # Top-left
        ControlPoint(x2, y1, 'corner_tr', zone.id),  # Top-right
        ControlPoint(x2, y2, 'corner_br', zone.id),  # Bottom-right
        ControlPoint(x1, y2, 'corner_bl', zone.id),  # Bottom-left
    ]
    
    # Edge midpoint control points
    mid_x, mid_y = x1 + zone.width / 2, y1 + zone.height / 2
    edge_points = [
        ControlPoint(mid_x, y1, 'edge_top', zone.id),     # Top edge
        ControlPoint(x2, mid_y, 'edge_right', zone.id),   # Right edge
        ControlPoint(mid_x, y2, 'edge_bottom', zone.id),  # Bottom edge
        ControlPoint(x1, mid_y, 'edge_left', zone.id),    # Left edge
    ]
    
    # Verify control points
    assert len(corner_points) == 4, "Should have 4 corner control points"
    assert len(edge_points) == 4, "Should have 4 edge control points"
    
    # Verify corner positions
    assert corner_points[0].x == 0.2 and corner_points[0].y == 0.2, "Top-left corner incorrect"
    assert corner_points[1].x == 0.6 and corner_points[1].y == 0.2, "Top-right corner incorrect"
    assert corner_points[2].x == 0.6 and corner_points[2].y == 0.5, "Bottom-right corner incorrect"
    assert corner_points[3].x == 0.2 and corner_points[3].y == 0.5, "Bottom-left corner incorrect"
    
    # Verify edge midpoints
    assert edge_points[0].x == 0.4 and edge_points[0].y == 0.2, "Top edge midpoint incorrect"
    assert edge_points[1].x == 0.6 and edge_points[1].y == 0.35, "Right edge midpoint incorrect"
    
    print("✓ Control point creation and positioning verified")


def test_process_zone_association():
    """Test process-zone association and naming consistency"""
    print("\n=== Testing Process-Zone Association ===")
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    
    try:
        # Create managers
        pm = ProcessManager(temp_file)
        zm = ZoneManager("zones_test.json")
        
        # Create process
        process = pm.create_process("Test Process")
        process_number = process.id.split('_')[-1]
        
        # Create zones with correct naming
        pick_zone_name = f"Pick Zone {process_number}"
        drop_zone_name = f"Drop Zone {process_number}"
        
        pick_zone = zm.create_zone_direct(pick_zone_name, ZoneType.PICK, 0.1, 0.1, 0.3, 0.3)
        drop_zone = zm.create_zone_direct(drop_zone_name, ZoneType.DROP, 0.6, 0.6, 0.3, 0.3)
        
        # Associate zones
        success = pm.associate_zones(process.id, pick_zone.id, drop_zone.id)
        assert success, "Zone association failed"
        
        # Verify association
        pick_id, drop_id = pm.get_process_zone_ids(process.id)
        assert pick_id == pick_zone.id, "Pick zone association incorrect"
        assert drop_id == drop_zone.id, "Drop zone association incorrect"
        
        # Verify naming consistency
        assert pick_zone.name == f"Pick Zone {process_number}", "Pick zone naming inconsistent"
        assert drop_zone.name == f"Drop Zone {process_number}", "Drop zone naming inconsistent"
        
        print("✓ Process-zone association and naming verified")
        
        # Cleanup
        os.unlink("zones_test.json")
        
    finally:
        os.unlink(temp_file)
    
    print("✓ Process-zone association tests passed")


def main():
    """Run all tests"""
    print("NextSight v2 Manual Verification Test")
    print("=" * 40)
    
    try:
        test_process_persistence()
        test_zone_creation_and_editing()
        test_control_point_creation()
        test_process_zone_association()
        
        print("\n" + "=" * 40)
        print("✓ ALL TESTS PASSED")
        print("NextSight v2 zone editing and process management features are working correctly!")
        return 0
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())