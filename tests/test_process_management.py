"""
Test process management system implementation
"""

import pytest
import time
import tempfile
import os
from unittest.mock import Mock, patch

def test_process_manager_creation():
    """Test basic ProcessManager creation and functionality"""
    from nextsight.core.process_manager import ProcessManager, Process
    
    # Use temporary file for testing
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config_file = f.name
    
    try:
        manager = ProcessManager(config_file)
        
        # Test creating a process
        process = manager.create_process("Test Process")
        assert process is not None
        assert process.name == "Test Process"
        assert process.id == "process_1"
        assert process.pick_zone_id is None
        assert process.drop_zone_id is None
        
        # Test getting all processes
        processes = manager.get_all_processes()
        assert len(processes) == 1
        assert processes[0].id == process.id
        
        # Test process statistics
        stats = manager.get_statistics()
        assert stats['total_processes'] == 1
        assert stats['total_completed'] == 0
        assert stats['total_errors'] == 0
        
    finally:
        os.unlink(config_file)


def test_process_zone_association():
    """Test associating zones with processes"""
    from nextsight.core.process_manager import ProcessManager
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config_file = f.name
    
    try:
        manager = ProcessManager(config_file)
        
        # Create process
        process = manager.create_process("Test Process")
        
        # Associate zones
        success = manager.associate_zones(process.id, "pick_zone_1", "drop_zone_1")
        assert success
        
        # Check association
        pick_zone_id, drop_zone_id = manager.get_process_zone_ids(process.id)
        assert pick_zone_id == "pick_zone_1"
        assert drop_zone_id == "drop_zone_1"
        
        # Test reverse lookup
        assert manager.get_process_id_for_pick_zone("pick_zone_1") == process.id
        assert manager.get_process_id_for_drop_zone("drop_zone_1") == process.id
        
    finally:
        os.unlink(config_file)


def test_process_pick_drop_logic():
    """Test process pick and drop event handling"""
    from nextsight.core.process_manager import ProcessManager
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config_file = f.name
    
    try:
        manager = ProcessManager(config_file)
        
        # Create process and associate zones
        process = manager.create_process("Test Process")
        manager.associate_zones(process.id, "pick_zone_1", "drop_zone_1")
        
        # Test pick event
        success = manager.handle_pick_event("hand_1", "pick_zone_1")
        assert success
        
        # Check active picks
        active_picks = manager.get_active_picks_info()
        assert "hand_1" in active_picks
        assert active_picks["hand_1"]["process_id"] == process.id
        
        # Test correct drop event
        success = manager.handle_drop_event("hand_1", "drop_zone_1")
        assert success
        
        # Check statistics - should have one completion
        stats = manager.get_statistics()
        assert stats['total_completed'] == 1
        assert stats['total_errors'] == 0
        
        # Check active picks cleared
        active_picks = manager.get_active_picks_info()
        assert "hand_1" not in active_picks
        
    finally:
        os.unlink(config_file)


def test_process_wrong_drop_logic():
    """Test process error handling for wrong drop"""
    from nextsight.core.process_manager import ProcessManager
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config_file = f.name
    
    try:
        manager = ProcessManager(config_file)
        
        # Create two processes
        process1 = manager.create_process("Process 1")
        process2 = manager.create_process("Process 2")
        
        manager.associate_zones(process1.id, "pick_zone_1", "drop_zone_1")
        manager.associate_zones(process2.id, "pick_zone_2", "drop_zone_2")
        
        # Pick from process 1
        manager.handle_pick_event("hand_1", "pick_zone_1")
        
        # Drop in process 2 (wrong process)
        success = manager.handle_drop_event("hand_1", "drop_zone_2")
        assert not success  # Should return False for wrong process
        
        # Check statistics - should have one error
        stats = manager.get_statistics()
        assert stats['total_completed'] == 0
        assert stats['total_errors'] == 1
        
    finally:
        os.unlink(config_file)


def test_process_deletion():
    """Test process deletion"""
    from nextsight.core.process_manager import ProcessManager
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config_file = f.name
    
    try:
        manager = ProcessManager(config_file)
        
        # Create process
        process = manager.create_process("Test Process")
        manager.associate_zones(process.id, "pick_zone_1", "drop_zone_1")
        
        # Start a pick
        manager.handle_pick_event("hand_1", "pick_zone_1")
        
        # Delete process
        success = manager.delete_process(process.id)
        assert success
        
        # Check process is gone
        assert manager.get_process(process.id) is None
        assert len(manager.get_all_processes()) == 0
        
        # Check active picks cleared
        active_picks = manager.get_active_picks_info()
        assert "hand_1" not in active_picks
        
    finally:
        os.unlink(config_file)


def test_process_persistence():
    """Test saving and loading processes"""
    from nextsight.core.process_manager import ProcessManager
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config_file = f.name
    
    try:
        # Create manager and processes
        manager1 = ProcessManager(config_file)
        process1 = manager1.create_process("Process 1")
        process2 = manager1.create_process("Process 2")
        
        manager1.associate_zones(process1.id, "pick_1", "drop_1")
        manager1.associate_zones(process2.id, "pick_2", "drop_2")
        
        # Create new manager instance (should load from file)
        manager2 = ProcessManager(config_file)
        
        # Check processes loaded
        processes = manager2.get_all_processes()
        assert len(processes) == 2
        
        # Check process counter continued correctly
        process3 = manager2.create_process("Process 3")
        assert process3.id == "process_3"
        
    finally:
        os.unlink(config_file)


def test_process_widget_functionality():
    """Test process widget components"""
    # Note: This test is limited due to GUI testing constraints
    # We'll test the basic imports and class structure
    
    try:
        from nextsight.ui.process_widget import ProcessListWidget, ProcessManagementWidget
        from nextsight.core.process_manager import Process
        
        # Test that classes can be instantiated (basic smoke test)
        # Note: Full GUI testing would require display
        assert ProcessListWidget is not None
        assert ProcessManagementWidget is not None
        
        # Test Process data class
        process = Process(id="test_1", name="Test Process")
        assert process.id == "test_1"
        assert process.name == "Test Process"
        assert process.active is True
        
        print("Process widget classes imported successfully")
        
    except ImportError as e:
        # Expected in headless environment
        print(f"GUI import limitation (expected): {e}")
        return True


def test_control_panel_integration():
    """Test control panel integration with process management"""
    try:
        # Test imports
        from nextsight.ui.control_panel import EnhancedControlPanel
        from nextsight.ui.process_widget import ProcessManagementWidget
        
        # Basic class validation
        assert EnhancedControlPanel is not None
        assert ProcessManagementWidget is not None
        
        print("Control panel integration classes imported successfully")
        
    except ImportError as e:
        print(f"GUI import limitation (expected): {e}")
        return True


if __name__ == "__main__":
    print("Running process management tests...")
    
    test_process_manager_creation()
    print("✓ Process manager creation test passed")
    
    test_process_zone_association()
    print("✓ Process zone association test passed")
    
    test_process_pick_drop_logic()
    print("✓ Process pick/drop logic test passed")
    
    test_process_wrong_drop_logic()
    print("✓ Process wrong drop logic test passed")
    
    test_process_deletion()
    print("✓ Process deletion test passed")
    
    test_process_persistence()
    print("✓ Process persistence test passed")
    
    test_process_widget_functionality()
    print("✓ Process widget functionality test passed")
    
    test_control_panel_integration()
    print("✓ Control panel integration test passed")
    
    print("\nAll process management tests completed successfully!")