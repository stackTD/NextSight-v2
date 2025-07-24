#!/usr/bin/env python3
"""
NextSight v2 Process Management Demo
Demonstrates the process management system functionality
"""

import sys
import os
import tempfile

# Add project root to path
sys.path.insert(0, '/home/runner/work/NextSight-v2/NextSight-v2')

def demo_process_management():
    """Demonstrate core process management functionality"""
    print("=" * 60)
    print("NextSight v2 Process Management System Demo")
    print("=" * 60)
    
    # Import the core process manager (without GUI dependencies)
    from tests.test_process_core import TestProcessManager
    
    # Use temporary file for demo
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config_file = f.name
    
    try:
        print("\n1. Creating Process Manager...")
        manager = TestProcessManager(config_file)
        print(f"   ✓ Process Manager initialized with config: {config_file}")
        
        print("\n2. Creating processes...")
        process1 = manager.create_process("Assembly Line A")
        process2 = manager.create_process("Quality Control")
        process3 = manager.create_process("Packaging")
        
        print(f"   ✓ Created process: {process1.name} (ID: {process1.id})")
        print(f"   ✓ Created process: {process2.name} (ID: {process2.id})")
        print(f"   ✓ Created process: {process3.name} (ID: {process3.id})")
        
        print("\n3. Associating zones with processes...")
        manager.associate_zones(process1.id, "pick_zone_assembly", "drop_zone_assembly")
        manager.associate_zones(process2.id, "pick_zone_qc", "drop_zone_qc")
        manager.associate_zones(process3.id, "pick_zone_packaging", "drop_zone_packaging")
        
        print(f"   ✓ Process '{process1.name}' zones: pick_zone_assembly → drop_zone_assembly")
        print(f"   ✓ Process '{process2.name}' zones: pick_zone_qc → drop_zone_qc")
        print(f"   ✓ Process '{process3.name}' zones: pick_zone_packaging → drop_zone_packaging")
        
        print("\n4. Simulating workflow operations...")
        
        # Simulate successful workflow
        print("\n   Scenario 1: Successful workflow")
        print("   - Hand picks from assembly pick zone")
        manager.handle_pick_event("worker_hand_1", "pick_zone_assembly")
        
        print("   - Hand drops in assembly drop zone")
        success = manager.handle_drop_event("worker_hand_1", "drop_zone_assembly")
        if success:
            print("   ✓ SUCCESS: Assembly Line A process completed!")
        
        # Simulate wrong process error
        print("\n   Scenario 2: Wrong process error")
        print("   - Hand picks from QC pick zone")
        manager.handle_pick_event("worker_hand_2", "pick_zone_qc")
        
        print("   - Hand drops in packaging drop zone (WRONG!)")
        success = manager.handle_drop_event("worker_hand_2", "drop_zone_packaging")
        if not success:
            print("   ✗ ERROR: Wrong process! Hand picked from QC but dropped in Packaging")
        
        # Another successful workflow
        print("\n   Scenario 3: Another successful workflow")
        print("   - Hand picks from packaging pick zone")
        manager.handle_pick_event("worker_hand_3", "pick_zone_packaging")
        
        print("   - Hand drops in packaging drop zone")
        success = manager.handle_drop_event("worker_hand_3", "drop_zone_packaging")
        if success:
            print("   ✓ SUCCESS: Packaging process completed!")
        
        print("\n5. Process statistics...")
        stats = manager.get_statistics()
        print(f"   Total processes: {stats['total_processes']}")
        print(f"   Total completed operations: {stats['total_completed']}")
        print(f"   Total errors: {stats['total_errors']}")
        print(f"   Success rate: {stats['success_rate']:.1f}%")
        
        print("\n6. Active picks tracking...")
        active_picks = manager.get_active_picks_info()
        if active_picks:
            print("   Active picks:")
            for hand_id, info in active_picks.items():
                print(f"   - {hand_id}: picked from {info['pick_zone_id']} (process: {info['process_name']})")
        else:
            print("   No active picks")
        
        print("\n7. Process deletion...")
        print(f"   Deleting process: {process2.name}")
        manager.delete_process(process2.id)
        
        remaining_processes = manager.get_all_processes()
        print(f"   Remaining processes: {len(remaining_processes)}")
        for p in remaining_processes:
            print(f"   - {p.name} (completed: {p.completed_count}, errors: {p.error_count})")
        
        print("\n8. Persistence test...")
        print("   Saving processes to file...")
        manager.save_processes()
        
        print("   Creating new manager instance...")
        manager2 = TestProcessManager(config_file)
        loaded_processes = manager2.get_all_processes()
        
        print(f"   Loaded {len(loaded_processes)} processes from file:")
        for p in loaded_processes:
            print(f"   - {p.name} (ID: {p.id})")
        
        print("\n" + "=" * 60)
        print("✓ Process Management System Demo Completed Successfully!")
        print("=" * 60)
        
        print("\nKey Features Demonstrated:")
        print("• Process creation and management")
        print("• Zone association with processes")
        print("• Pick and drop workflow validation")
        print("• Wrong process error detection")
        print("• Statistics tracking")
        print("• Hand consistency enforcement")
        print("• Process deletion and cleanup")
        print("• Configuration persistence")
        
    finally:
        # Cleanup
        os.unlink(config_file)


if __name__ == "__main__":
    demo_process_management()