#!/usr/bin/env python3
"""
Test script to verify the fixes for the four zone system issues
"""

import sys
import os
import time
import logging

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_counter_increment_fix():
    """Test Issue #3 FIX: Pick and drop counter incremental issue"""
    print("Testing counter increment fix...")
    
    try:
        from nextsight.zones.zone_manager import ZoneManager
        from nextsight.zones.zone_config import ZoneType
        
        # Create temporary test zone manager
        manager = ZoneManager("/tmp/test_zones_counter.json")
        
        # Create a pick zone for testing
        zone = manager.create_zone_direct("Test Pick Zone", ZoneType.PICK, 0.2, 0.2, 0.3, 0.3)
        
        initial_picks = manager.session_stats['total_picks']
        
        # Simulate multiple rapid enter events for same hand/zone (old issue)
        events = [
            {'type': 'hand_enter_zone', 'zone_type': 'pick', 'hand_id': 'left_0', 'zone_id': zone.id, 'timestamp': time.time()},
            {'type': 'hand_enter_zone', 'zone_type': 'pick', 'hand_id': 'left_0', 'zone_id': zone.id, 'timestamp': time.time() + 0.1},
            {'type': 'hand_enter_zone', 'zone_type': 'pick', 'hand_id': 'left_0', 'zone_id': zone.id, 'timestamp': time.time() + 0.2},
        ]
        
        # Process events individually (simulating rapid detection)
        for event in events:
            manager.process_interaction_events([event])
        
        final_picks = manager.session_stats['total_picks']
        picks_incremented = final_picks - initial_picks
        
        if picks_incremented == 1:
            print("✓ FIXED: Counter only incremented once for stable hand")
            return True
        else:
            print(f"✗ ISSUE REMAINS: Counter incremented {picks_incremented} times")
            return False
            
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

def test_hand_consistency_fix():
    """Test Issue #4 FIX: Pick and drop hand consistency issue"""
    print("Testing hand consistency fix...")
    
    try:
        from nextsight.zones.zone_manager import ZoneManager
        from nextsight.zones.zone_config import ZoneType
        
        # Create temporary test zone manager
        manager = ZoneManager("/tmp/test_zones_consistency.json")
        
        # Create pick and drop zones for testing
        pick_zone = manager.create_zone_direct("Test Pick Zone", ZoneType.PICK, 0.2, 0.2, 0.3, 0.3)
        drop_zone = manager.create_zone_direct("Test Drop Zone", ZoneType.DROP, 0.6, 0.6, 0.3, 0.3)
        
        initial_picks = manager.session_stats['total_picks']
        initial_drops = manager.session_stats['total_drops']
        
        # Test 1: Pick with right hand, try drop with left hand (should be rejected)
        pick_event = {
            'type': 'pick_gesture_detected', 
            'hand_id': 'right_0', 
            'zone_id': pick_zone.id, 
            'gesture': 'pinch',
            'timestamp': time.time()
        }
        
        drop_event_wrong_hand = {
            'type': 'drop_gesture_detected', 
            'hand_id': 'left_0',  # Different hand!
            'zone_id': drop_zone.id, 
            'gesture': 'open',
            'timestamp': time.time() + 1.0
        }
        
        drop_event_correct_hand = {
            'type': 'drop_gesture_detected', 
            'hand_id': 'right_0',  # Same hand as pick
            'zone_id': drop_zone.id, 
            'gesture': 'open',
            'timestamp': time.time() + 2.0
        }
        
        # Process pick event
        manager.process_interaction_events([pick_event])
        picks_after_pick = manager.session_stats['total_picks']
        
        # Try drop with wrong hand
        manager.process_interaction_events([drop_event_wrong_hand])
        drops_after_wrong = manager.session_stats['total_drops']
        
        # Try drop with correct hand
        manager.process_interaction_events([drop_event_correct_hand])
        drops_after_correct = manager.session_stats['total_drops']
        
        pick_count = picks_after_pick - initial_picks
        wrong_drop_count = drops_after_wrong - initial_drops
        correct_drop_count = drops_after_correct - initial_drops
        
        if pick_count == 1 and wrong_drop_count == 0 and correct_drop_count == 1:
            print("✓ FIXED: Hand consistency enforced - wrong hand drop rejected, correct hand drop accepted")
            
            # Check that hand consistency tracking is cleared after successful drop
            consistency_status = manager.get_hand_consistency_status()
            if len(consistency_status['active_picks']) == 0:
                print("✓ FIXED: Hand consistency tracking cleared after successful drop")
                return True
            else:
                print("✗ PARTIAL FIX: Hand consistency enforced but tracking not cleared")
                return False
        else:
            print(f"✗ ISSUE REMAINS: Pick count: {pick_count}, Wrong drop count: {wrong_drop_count}, Correct drop count: {correct_drop_count}")
            return False
            
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

def test_gesture_cooldown_fix():
    """Test gesture cooldown to prevent rapid event generation"""
    print("Testing gesture cooldown fix...")
    
    try:
        from nextsight.zones.intersection_detector import IntersectionDetector
        from nextsight.zones.zone_config import Zone, ZoneType
        
        detector = IntersectionDetector()
        
        # Test gesture cooldown functionality
        hand_id = "test_hand"
        
        # First gesture should be allowed
        can_generate_1 = detector._can_generate_gesture_event(hand_id, 'pick')
        
        # Update cooldown
        detector._update_gesture_cooldown(hand_id, 'pick')
        
        # Immediate second gesture should be blocked
        can_generate_2 = detector._can_generate_gesture_event(hand_id, 'pick')
        
        if can_generate_1 and not can_generate_2:
            print("✓ FIXED: Gesture cooldown prevents rapid duplicate events")
            return True
        else:
            print(f"✗ ISSUE REMAINS: Cooldown not working - first: {can_generate_1}, second: {can_generate_2}")
            return False
            
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

def test_zone_deletion_signals():
    """Test zone deletion signal emission"""
    print("Testing zone deletion signals...")
    
    try:
        from nextsight.zones.zone_manager import ZoneManager
        from nextsight.zones.zone_config import ZoneType
        
        # Track emitted signals
        deleted_signals = []
        
        def track_deletion(zone_id):
            deleted_signals.append(zone_id)
        
        # Create temporary test zone manager
        manager = ZoneManager("/tmp/test_zones_deletion.json")
        manager.zone_deleted.connect(track_deletion)
        
        # Create a test zone
        zone = manager.create_zone_direct("Test Zone", ZoneType.PICK, 0.2, 0.2, 0.3, 0.3)
        zone_id = zone.id
        
        initial_zone_count = len(manager.get_zones())
        
        # Delete the zone
        success = manager.delete_zone(zone_id)
        
        final_zone_count = len(manager.get_zones())
        
        if success and zone_id in deleted_signals and final_zone_count == initial_zone_count - 1:
            print("✓ CONFIRMED: Zone deletion signals working correctly")
            return True
        else:
            print(f"✗ ISSUE: Deletion success: {success}, Signal emitted: {zone_id in deleted_signals}, Zone count: {initial_zone_count} -> {final_zone_count}")
            return False
            
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

def run_fix_verification():
    """Run all fix verification tests"""
    print("NextSight v2 - Zone System Fix Verification")
    print("=" * 45)
    print()
    
    tests = [
        test_counter_increment_fix,
        test_hand_consistency_fix,
        test_gesture_cooldown_fix,
        test_zone_deletion_signals
    ]
    
    fixes_working = 0
    total_tests = len(tests)
    
    for test in tests:
        try:
            if test():
                fixes_working += 1
            print()
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            print()
    
    print("=" * 45)
    print(f"Fixes verified: {fixes_working}/{total_tests}")
    
    if fixes_working == total_tests:
        print("🎉 All fixes verified successfully!")
        print()
        print("Fixed issues:")
        print("✓ Counter increment issue - Fixed")
        print("✓ Hand consistency tracking - Implemented") 
        print("✓ Gesture cooldown prevention - Fixed")
        print("✓ Zone deletion signals - Working")
        print()
        print("System ready for testing! 🚀")
        return 0
    else:
        remaining_issues = total_tests - fixes_working
        print(f"❌ {remaining_issues} issues still need attention")
        return remaining_issues

if __name__ == "__main__":
    issues = run_fix_verification()
    sys.exit(0 if issues == 0 else 1)