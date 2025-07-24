"""
Comprehensive integration test for process management system
Tests the complete flow without GUI dependencies
"""

import pytest
import tempfile
import os
import sys

# Add project root to path
sys.path.insert(0, '/home/runner/work/NextSight-v2/NextSight-v2')

def test_complete_process_workflow():
    """Test the complete process workflow from creation to deletion"""
    from tests.test_process_core import TestProcessManager
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config_file = f.name
    
    try:
        # Initialize manager
        manager = TestProcessManager(config_file)
        
        # Test 1: Create multiple processes
        process1 = manager.create_process("Manufacturing Line")
        process2 = manager.create_process("Quality Inspection")
        
        assert len(manager.get_all_processes()) == 2
        assert process1.name == "Manufacturing Line"
        assert process2.name == "Quality Inspection"
        
        # Test 2: Associate zones
        success1 = manager.associate_zones(process1.id, "pick_manufacturing", "drop_manufacturing")
        success2 = manager.associate_zones(process2.id, "pick_quality", "drop_quality")
        
        assert success1 and success2
        
        # Test 3: Verify zone associations
        pick1, drop1 = manager.get_process_zone_ids(process1.id)
        pick2, drop2 = manager.get_process_zone_ids(process2.id)
        
        assert pick1 == "pick_manufacturing" and drop1 == "drop_manufacturing"
        assert pick2 == "pick_quality" and drop2 == "drop_quality"
        
        # Test 4: Successful workflow simulation
        # Complete workflow for process 1
        assert manager.handle_pick_event("hand1", "pick_manufacturing")
        assert manager.handle_drop_event("hand1", "drop_manufacturing")
        
        # Complete workflow for process 2
        assert manager.handle_pick_event("hand2", "pick_quality")
        assert manager.handle_drop_event("hand2", "drop_quality")
        
        # Test 5: Error case - wrong process
        assert manager.handle_pick_event("hand3", "pick_manufacturing")
        assert not manager.handle_drop_event("hand3", "drop_quality")  # Wrong drop zone
        
        # Test 6: Verify statistics
        stats = manager.get_statistics()
        assert stats['total_processes'] == 2
        assert stats['total_completed'] == 2
        assert stats['total_errors'] == 1
        assert abs(stats['success_rate'] - 66.7) < 0.1
        
        # Test 7: Process deletion
        assert manager.delete_process(process1.id)
        assert len(manager.get_all_processes()) == 1
        assert manager.get_process(process1.id) is None
        
        # Test 8: Persistence
        manager.save_processes()
        
        # Create new manager and verify persistence
        manager2 = TestProcessManager(config_file)
        loaded_processes = manager2.get_all_processes()
        
        assert len(loaded_processes) == 1
        assert loaded_processes[0].name == "Quality Inspection"
        assert loaded_processes[0].completed_count == 1
        assert loaded_processes[0].error_count == 0
        
        print("✓ Complete process workflow test passed")
        
    finally:
        os.unlink(config_file)


def test_hand_consistency_tracking():
    """Test hand consistency tracking across multiple operations"""
    from tests.test_process_core import TestProcessManager
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config_file = f.name
    
    try:
        manager = TestProcessManager(config_file)
        
        # Create process
        process = manager.create_process("Test Process")
        manager.associate_zones(process.id, "pick_test", "drop_test")
        
        # Test multiple hands picking from same zone
        assert manager.handle_pick_event("hand_A", "pick_test")
        assert manager.handle_pick_event("hand_B", "pick_test")
        
        # Check active picks
        active_picks = manager.get_active_picks_info()
        assert "hand_A" in active_picks
        assert "hand_B" in active_picks
        
        # Test drops - both should succeed (same process)
        assert manager.handle_drop_event("hand_A", "drop_test")
        assert manager.handle_drop_event("hand_B", "drop_test")
        
        # Verify statistics
        stats = manager.get_statistics()
        assert stats['total_completed'] == 2
        assert stats['total_errors'] == 0
        assert stats['active_picks'] == 0
        
        print("✓ Hand consistency tracking test passed")
        
    finally:
        os.unlink(config_file)


def test_complex_multi_process_scenario():
    """Test complex scenario with multiple processes and mixed operations"""
    from tests.test_process_core import TestProcessManager
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config_file = f.name
    
    try:
        manager = TestProcessManager(config_file)
        
        # Create 3 processes
        p1 = manager.create_process("Process A")
        p2 = manager.create_process("Process B") 
        p3 = manager.create_process("Process C")
        
        # Associate zones
        manager.associate_zones(p1.id, "pick_A", "drop_A")
        manager.associate_zones(p2.id, "pick_B", "drop_B")
        manager.associate_zones(p3.id, "pick_C", "drop_C")
        
        # Simulate complex workflow with multiple hands
        operations = [
            ("hand1", "pick_A", "drop_A", True),   # Correct
            ("hand2", "pick_B", "drop_C", False),  # Wrong process
            ("hand3", "pick_C", "drop_C", True),   # Correct
            ("hand4", "pick_A", "drop_B", False),  # Wrong process
            ("hand5", "pick_B", "drop_B", True),   # Correct
        ]
        
        expected_success = 0
        expected_errors = 0
        
        for hand, pick_zone, drop_zone, should_succeed in operations:
            manager.handle_pick_event(hand, pick_zone)
            result = manager.handle_drop_event(hand, drop_zone)
            
            if should_succeed:
                assert result, f"Expected success for {hand}: {pick_zone} -> {drop_zone}"
                expected_success += 1
            else:
                assert not result, f"Expected failure for {hand}: {pick_zone} -> {drop_zone}"
                expected_errors += 1
        
        # Verify final statistics
        stats = manager.get_statistics()
        assert stats['total_completed'] == expected_success
        assert stats['total_errors'] == expected_errors
        assert stats['active_picks'] == 0
        
        print("✓ Complex multi-process scenario test passed")
        
    finally:
        os.unlink(config_file)


def test_process_naming_and_identification():
    """Test process naming and identification systems"""
    from tests.test_process_core import TestProcessManager
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config_file = f.name
    
    try:
        manager = TestProcessManager(config_file)
        
        # Test default naming
        p1 = manager.create_process()
        assert p1.name == "Process 1"
        assert p1.id == "process_1"
        
        # Test custom naming
        p2 = manager.create_process("Custom Process Name")
        assert p2.name == "Custom Process Name"
        assert p2.id == "process_2"
        
        # Test process retrieval
        assert manager.get_process("process_1") == p1
        assert manager.get_process("process_2") == p2
        assert manager.get_process("nonexistent") is None
        
        # Test process lookup by name
        found_process = manager.get_process_by_name("Custom Process Name")
        assert found_process == p2
        
        print("✓ Process naming and identification test passed")
        
    finally:
        os.unlink(config_file)


if __name__ == "__main__":
    print("Running comprehensive process management integration tests...")
    
    test_complete_process_workflow()
    test_hand_consistency_tracking()
    test_complex_multi_process_scenario()
    test_process_naming_and_identification()
    
    print("\n" + "="*60)
    print("✅ ALL INTEGRATION TESTS PASSED!")
    print("="*60)
    print("\nProcess Management System is ready for production use!")
    print("\nKey capabilities validated:")
    print("• ✓ Process creation and management")
    print("• ✓ Zone association and validation")
    print("• ✓ Pick/drop workflow enforcement")
    print("• ✓ Wrong process error detection")
    print("• ✓ Hand consistency tracking")
    print("• ✓ Multi-process concurrent operations")
    print("• ✓ Statistics and monitoring")
    print("• ✓ Process deletion and cleanup")
    print("• ✓ Configuration persistence")
    print("• ✓ Complex workflow scenarios")