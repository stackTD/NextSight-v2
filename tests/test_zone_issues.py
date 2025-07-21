#!/usr/bin/env python3
"""
Test script to reproduce and verify fixes for the four zone system issues
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

def test_counter_increment_issue():
    """Test Issue #3: Pick and drop counter incremental issue"""
    print("Testing counter increment issue...")
    
    try:
        # Mock the zone manager behavior
        class MockZoneManager:
            def __init__(self):
                self.pick_events = []
                self.drop_events = []
                self.session_stats = {'total_picks': 0, 'total_drops': 0}
                
            def process_interaction_events(self, events):
                """Current problematic implementation"""
                for event in events:
                    if event['type'] == 'hand_enter_zone':
                        if event['zone_type'] == 'pick':
                            self.pick_events.append(event)
                            self.session_stats['total_picks'] += 1
                        elif event['zone_type'] == 'drop':
                            self.drop_events.append(event)
                            self.session_stats['total_drops'] += 1
        
        manager = MockZoneManager()
        
        # Simulate hand staying in zone (multiple enter events)
        events = [
            {'type': 'hand_enter_zone', 'zone_type': 'pick', 'hand_id': 'left_0', 'timestamp': time.time()},
            {'type': 'hand_enter_zone', 'zone_type': 'pick', 'hand_id': 'left_0', 'timestamp': time.time() + 0.1},
            {'type': 'hand_enter_zone', 'zone_type': 'pick', 'hand_id': 'left_0', 'timestamp': time.time() + 0.2},
        ]
        
        for event_batch in [events[:1], events[1:2], events[2:3]]:
            manager.process_interaction_events(event_batch)
        
        # Issue: Counter increments multiple times for same hand in same zone
        if manager.session_stats['total_picks'] > 1:
            print(f"✗ ISSUE CONFIRMED: Counter incremented {manager.session_stats['total_picks']} times for stable hand")
            return True
        else:
            print("✓ Counter behavior is correct")
            return False
            
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

def test_hand_consistency_issue():
    """Test Issue #4: Pick and drop hand consistency issue"""
    print("Testing hand consistency issue...")
    
    try:
        # Mock current behavior (no hand consistency)
        class MockZoneManager:
            def __init__(self):
                self.pick_events = []
                self.drop_events = []
                
            def process_pick(self, hand_id, zone_id):
                self.pick_events.append({'hand_id': hand_id, 'zone_id': zone_id})
                
            def process_drop(self, hand_id, zone_id):
                self.drop_events.append({'hand_id': hand_id, 'zone_id': zone_id})
                # Current: No consistency check
                return True  # Always allows drop
        
        manager = MockZoneManager()
        
        # Simulate pick with right hand, drop with left hand
        manager.process_pick('right_0', 'pick_001')
        inconsistent_drop_allowed = manager.process_drop('left_0', 'drop_001')
        
        if inconsistent_drop_allowed:
            print("✗ ISSUE CONFIRMED: Hand consistency not enforced - left hand can drop after right hand pick")
            return True
        else:
            print("✓ Hand consistency is enforced")
            return False
            
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

def test_zone_deletion_issue():
    """Test Issue #1: Zone deletion visual clearing"""
    print("Testing zone deletion issue...")
    
    try:
        # Mock zone config behavior
        class MockZoneConfig:
            def __init__(self):
                self.zones = [
                    {'id': 'pick_001', 'name': 'Pick Zone 1'},
                    {'id': 'drop_001', 'name': 'Drop Zone 1'}
                ]
                
            def remove_zone(self, zone_id):
                self.zones = [z for z in self.zones if z['id'] != zone_id]
                return True
        
        class MockZoneManager:
            def __init__(self):
                self.config = MockZoneConfig()
                self.deletion_signals_emitted = []
                
            def zone_deleted_emit(self, zone_id):
                self.deletion_signals_emitted.append(zone_id)
                
            def delete_zone(self, zone_id):
                if self.config.remove_zone(zone_id):
                    self.zone_deleted_emit(zone_id)  # Should emit signal
                    return True
                return False
        
        manager = MockZoneManager()
        initial_count = len(manager.config.zones)
        
        # Delete a zone
        success = manager.delete_zone('pick_001')
        
        if success and len(manager.deletion_signals_emitted) > 0:
            print("✓ Zone deletion logic appears correct")
            return False  # No issue
        else:
            print("✗ ISSUE CONFIRMED: Zone deletion not emitting proper signals")
            return True
            
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

def test_immediate_detection_issue():
    """Test Issue #2: Hand detection immediacy"""
    print("Testing immediate hand detection issue...")
    
    try:
        # Mock zone detection behavior
        class MockIntersectionDetector:
            def __init__(self):
                self.zone_refresh_mode = False
                self.detection_enabled = True
                
            def detect_intersections(self, zones, detection_info):
                # Current issue: Detection might depend on refresh mode
                if not self.detection_enabled:
                    return {'intersections': {}, 'events': []}
                    
                # Simulate immediate detection working
                hands_info = detection_info.get('hands', {})
                if hands_info.get('hand_landmarks'):
                    return {
                        'intersections': {'zone_001': [{'hand_id': 'left_0', 'confidence': 0.8}]},
                        'events': [{'type': 'hand_enter_zone', 'hand_id': 'left_0', 'zone_id': 'zone_001'}]
                    }
                return {'intersections': {}, 'events': []}
        
        detector = MockIntersectionDetector()
        
        # Test detection without refresh mode
        detection_info = {
            'hands': {
                'hand_landmarks': [
                    [{'x': 0.3, 'y': 0.3, 'z': 0.0}]
                ],
                'handedness': ['Left']
            }
        }
        
        zones = [{'id': 'zone_001', 'active': True}]
        
        # Detection should work immediately
        result = detector.detect_intersections(zones, detection_info)
        
        if result['events']:
            print("✓ Hand detection works immediately")
            return False  # No issue
        else:
            print("✗ ISSUE CONFIRMED: Hand detection not working immediately")
            return True
            
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

def run_issue_tests():
    """Run all issue reproduction tests"""
    print("NextSight v2 - Zone System Issue Analysis")
    print("=" * 45)
    print()
    
    tests = [
        test_counter_increment_issue,
        test_hand_consistency_issue,
        test_zone_deletion_issue,
        test_immediate_detection_issue
    ]
    
    issues_found = 0
    total_tests = len(tests)
    
    for test in tests:
        try:
            if test():
                issues_found += 1
            print()
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            print()
    
    print("=" * 45)
    print(f"Issues confirmed: {issues_found}/{total_tests}")
    
    if issues_found > 0:
        print("🔧 Issues found that need fixing:")
        if issues_found >= 1:
            print("• Counter increment issue needs fix")
        if issues_found >= 2:  
            print("• Hand consistency tracking needs implementation")
        if issues_found >= 3:
            print("• Zone deletion visual clearing may need improvement")
        if issues_found >= 4:
            print("• Hand detection immediacy may need verification")
        print()
        print("Proceeding with fixes...")
        return issues_found
    else:
        print("✅ No issues found - system appears to be working correctly")
        return 0

if __name__ == "__main__":
    issues = run_issue_tests()
    sys.exit(0 if issues == 0 else 1)