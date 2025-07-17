"""
Hand-zone intersection detection for NextSight v2
Real-time detection when hands enter/exit zones with confidence validation
"""

import time
from typing import Dict, List, Optional, Tuple
from nextsight.zones.zone_config import Zone, ZoneType
from nextsight.utils.geometry import (
    ZoneIntersectionCalculator, Rectangle, Point, 
    HandLandmarkProcessor
)
import logging


class HandZoneState:
    """State tracking for hand-zone interactions"""
    
    def __init__(self, hand_id: str, zone_id: str):
        self.hand_id = hand_id
        self.zone_id = zone_id
        self.is_inside = False
        self.entry_time: Optional[float] = None
        self.exit_time: Optional[float] = None
        self.confidence_history: List[float] = []
        self.stability_count = 0
        self.required_stability = 5  # Increased frames needed for stable detection
        self.last_event_time = 0.0  # Track last event to prevent rapid firing
        self.min_event_interval = 1.0  # Minimum seconds between events
    
    def update_confidence(self, confidence: float) -> bool:
        """Update confidence and return if state should change"""
        current_time = time.time()
        
        self.confidence_history.append(confidence)
        
        # Keep only recent history
        if len(self.confidence_history) > 15:
            self.confidence_history.pop(0)
        
        # Check for stable high confidence (entering zone)
        if not self.is_inside:
            recent_high = sum(1 for c in self.confidence_history[-self.required_stability:] 
                            if c > 0.6)
            if recent_high >= self.required_stability and (current_time - self.last_event_time) >= self.min_event_interval:
                self.is_inside = True
                self.entry_time = current_time
                self.last_event_time = current_time
                self.stability_count = 0
                return True
        
        # Check for stable low confidence (exiting zone)
        else:
            recent_low = sum(1 for c in self.confidence_history[-self.required_stability:] 
                           if c < 0.3)
            if recent_low >= self.required_stability and (current_time - self.last_event_time) >= self.min_event_interval:
                self.is_inside = False
                self.exit_time = current_time
                self.last_event_time = current_time
                self.stability_count = 0
                return True
        
        return False
    
    def get_duration_inside(self) -> float:
        """Get duration hand has been inside zone"""
        if self.is_inside and self.entry_time:
            return time.time() - self.entry_time
        elif self.exit_time and self.entry_time:
            return self.exit_time - self.entry_time
        return 0.0


class IntersectionDetector:
    """Real-time hand-zone intersection detection with confidence validation"""
    
    def __init__(self):
        self.calculator = ZoneIntersectionCalculator()
        self.hand_processor = HandLandmarkProcessor()
        
        # State tracking
        self.hand_zone_states: Dict[str, HandZoneState] = {}
        self.active_intersections: Dict[str, List[str]] = {}  # zone_id -> [hand_ids]
        
        # Event callbacks
        self.on_hand_enter_zone = None
        self.on_hand_exit_zone = None
        
        # Performance settings
        self.detection_method = 'hybrid'  # 'point', 'bounding_box', 'hybrid'
        self.confidence_threshold = 0.6
        
        # Gesture detection cooldown tracking
        self.last_gesture_events = {}  # hand_id -> {gesture_type: timestamp}
        self.gesture_cooldown = 2.0  # Minimum seconds between same gesture events
        
        self.logger = logging.getLogger(__name__)
    
    def set_event_callbacks(self, on_enter=None, on_exit=None):
        """Set callbacks for zone entry/exit events"""
        self.on_hand_enter_zone = on_enter
        self.on_hand_exit_zone = on_exit
    
    def detect_intersections(self, zones: List[Zone], detection_info: Dict) -> Dict:
        """
        Detect hand-zone intersections for current frame
        
        Args:
            zones: List of active zones to check
            detection_info: Hand detection information from camera thread
            
        Returns:
            Dict with intersection results and events
        """
        results = {
            'intersections': {},
            'events': [],
            'statistics': {}
        }
        
        if not zones or 'hands' not in detection_info:
            if zones and 'hands' not in detection_info:
                self.logger.debug("No hands data in detection_info")
            return results
        
        hands_info = detection_info['hands']
        if not hands_info.get('hand_landmarks'):
            self.logger.debug("No hand_landmarks in hands_info")
            return results
        
        # Process each hand
        landmarks_list = hands_info['hand_landmarks']
        handedness_list = hands_info.get('handedness', [])
        
        self.logger.debug(f"Processing {len(landmarks_list)} hands with {len(zones)} zones")
        
        for hand_idx, landmarks in enumerate(landmarks_list):
            if landmarks is None:
                continue
            
            # Get hand identifier
            hand_type = 'unknown'
            if hand_idx < len(handedness_list):
                hand_type = handedness_list[hand_idx].lower()
            
            hand_id = f"{hand_type}_{hand_idx}"
            
            # Check intersection with each zone
            for zone in zones:
                if not zone.active:
                    continue
                
                zone_rect = Rectangle(zone.x, zone.y, zone.width, zone.height)
                intersection_result = self._detect_hand_zone_intersection(
                    landmarks, zone_rect, zone.confidence_threshold
                )
                
                # Detect hand gesture for interaction events
                gesture = self.hand_processor.detect_hand_gesture(landmarks)
                intersection_result['gesture'] = gesture
                
                # Update state and check for events
                state_key = f"{hand_id}_{zone.id}"
                if state_key not in self.hand_zone_states:
                    self.hand_zone_states[state_key] = HandZoneState(hand_id, zone.id)
                
                state = self.hand_zone_states[state_key]
                state_changed = state.update_confidence(intersection_result['confidence'])
                
                # Record current intersection
                if zone.id not in results['intersections']:
                    results['intersections'][zone.id] = []
                
                if state.is_inside:
                    results['intersections'][zone.id].append({
                        'hand_id': hand_id,
                        'confidence': intersection_result['confidence'],
                        'duration': state.get_duration_inside(),
                        'method': intersection_result['method'],
                        'gesture': gesture
                    })
                
                # Generate events on state change or gesture
                if state_changed or (state.is_inside and gesture in ['pinch', 'closed', 'open']):
                    event = self._create_intersection_event(
                        hand_id, zone, state, intersection_result
                    )
                    results['events'].append(event)
                    
                    # Log interaction events for debugging
                    if state_changed:
                        event_type = "entered" if state.is_inside else "exited"
                        self.logger.info(f"Hand {hand_id} {event_type} zone {zone.id} (confidence: {intersection_result['confidence']:.2f}, gesture: {gesture})")
                    elif gesture in ['pinch', 'closed']:
                        # Check gesture cooldown before creating pick event
                        if self._can_generate_gesture_event(hand_id, 'pick'):
                            self.logger.info(f"Pick gesture detected: {hand_id} in zone {zone.id} (gesture: {gesture})")
                            # Create pick event
                            pick_event = event.copy()
                            pick_event['type'] = 'pick_gesture_detected'
                            pick_event['gesture'] = gesture
                            results['events'].append(pick_event)
                            
                            # Update gesture cooldown
                            self._update_gesture_cooldown(hand_id, 'pick')
                        else:
                            self.logger.debug(f"Pick gesture cooldown active for {hand_id}")
                            
                    elif gesture == 'open':
                        # Check gesture cooldown before creating drop event
                        if self._can_generate_gesture_event(hand_id, 'drop'):
                            self.logger.info(f"Drop gesture detected: {hand_id} in zone {zone.id} (gesture: {gesture})")
                            # Create drop event
                            drop_event = event.copy()
                            drop_event['type'] = 'drop_gesture_detected'
                            drop_event['gesture'] = gesture
                            results['events'].append(drop_event)
                            
                            # Update gesture cooldown
                            self._update_gesture_cooldown(hand_id, 'drop')
                        else:
                            self.logger.debug(f"Drop gesture cooldown active for {hand_id}")
                    
                    # Update zone state
                    if state.is_inside:
                        zone.add_hand(hand_id)
                        zone.last_interaction = time.time()
                    else:
                        zone.remove_hand(hand_id)
                    
                    # Trigger callbacks
                    if state.is_inside and self.on_hand_enter_zone:
                        self.on_hand_enter_zone(hand_id, zone, intersection_result)
                    elif not state.is_inside and self.on_hand_exit_zone:
                        self.on_hand_exit_zone(hand_id, zone, state.get_duration_inside())
        
        # Update active intersections tracking
        self._update_active_intersections(results['intersections'])
        
        # Generate statistics
        results['statistics'] = self._generate_statistics(zones)
        
        return results
    
    def _detect_hand_zone_intersection(self, landmarks, zone_rect: Rectangle, 
                                     confidence_threshold: float) -> Dict:
        """Detect intersection using configured method"""
        if self.detection_method == 'point':
            return self.calculator.point_in_zone_intersection(
                landmarks, zone_rect, confidence_threshold
            )
        elif self.detection_method == 'bounding_box':
            return self.calculator.bounding_box_intersection(
                landmarks, zone_rect, confidence_threshold
            )
        else:  # hybrid
            return self.calculator.hybrid_intersection(
                landmarks, zone_rect, confidence_threshold
            )
    
    def _create_intersection_event(self, hand_id: str, zone: Zone, 
                                 state: HandZoneState, intersection_result: Dict) -> Dict:
        """Create event for zone entry/exit"""
        return {
            'type': 'hand_enter_zone' if state.is_inside else 'hand_exit_zone',
            'timestamp': time.time(),
            'hand_id': hand_id,
            'zone_id': zone.id,
            'zone_name': zone.name,
            'zone_type': zone.zone_type.value,
            'confidence': intersection_result['confidence'],
            'duration': state.get_duration_inside() if not state.is_inside else 0.0,
            'method': intersection_result['method']
        }
    
    def _update_active_intersections(self, intersections: Dict):
        """Update active intersections tracking"""
        self.active_intersections = {}
        
        for zone_id, hand_data in intersections.items():
            if hand_data:
                self.active_intersections[zone_id] = [h['hand_id'] for h in hand_data]
    
    def _generate_statistics(self, zones: List[Zone]) -> Dict:
        """Generate intersection statistics"""
        stats = {
            'total_zones': len(zones),
            'active_zones': len([z for z in zones if z.active]),
            'zones_with_hands': len(self.active_intersections),
            'total_hands_in_zones': sum(len(hands) for hands in self.active_intersections.values()),
            'pick_zones_active': 0,
            'drop_zones_active': 0,
            'detection_method': self.detection_method,
            'confidence_threshold': self.confidence_threshold
        }
        
        # Count active zones by type
        for zone_id in self.active_intersections:
            zone = next((z for z in zones if z.id == zone_id), None)
            if zone:
                if zone.zone_type == ZoneType.PICK:
                    stats['pick_zones_active'] += 1
                elif zone.zone_type == ZoneType.DROP:
                    stats['drop_zones_active'] += 1
        
        return stats
    
    def get_zone_status(self, zone_id: str) -> Dict:
        """Get detailed status for specific zone"""
        hands_in_zone = self.active_intersections.get(zone_id, [])
        
        status = {
            'zone_id': zone_id,
            'has_hands': len(hands_in_zone) > 0,
            'hand_count': len(hands_in_zone),
            'hands': hands_in_zone,
            'states': {}
        }
        
        # Get detailed state for each hand in zone
        for hand_id in hands_in_zone:
            state_key = f"{hand_id}_{zone_id}"
            if state_key in self.hand_zone_states:
                state = self.hand_zone_states[state_key]
                status['states'][hand_id] = {
                    'duration': state.get_duration_inside(),
                    'entry_time': state.entry_time,
                    'recent_confidence': state.confidence_history[-3:] if state.confidence_history else []
                }
        
        return status
    
    def reset_zone_states(self, zone_id: str = None):
        """Reset state tracking for zone(s)"""
        if zone_id:
            # Reset specific zone
            keys_to_remove = [key for key in self.hand_zone_states.keys() 
                            if key.endswith(f"_{zone_id}")]
            for key in keys_to_remove:
                del self.hand_zone_states[key]
        else:
            # Reset all zones
            self.hand_zone_states.clear()
            self.active_intersections.clear()
    
    def set_detection_method(self, method: str):
        """Set intersection detection method"""
        if method in ['point', 'bounding_box', 'hybrid']:
            self.detection_method = method
            self.logger.info(f"Intersection detection method set to: {method}")
    
    def set_confidence_threshold(self, threshold: float):
        """Set global confidence threshold"""
        self.confidence_threshold = max(0.1, min(1.0, threshold))
        self.logger.info(f"Intersection confidence threshold set to: {self.confidence_threshold}")
    
    def _can_generate_gesture_event(self, hand_id: str, gesture_type: str) -> bool:
        """Check if enough time has passed to generate another gesture event"""
        current_time = time.time()
        
        if hand_id not in self.last_gesture_events:
            return True
        
        last_gesture_time = self.last_gesture_events[hand_id].get(gesture_type, 0.0)
        return (current_time - last_gesture_time) >= self.gesture_cooldown
    
    def _update_gesture_cooldown(self, hand_id: str, gesture_type: str):
        """Update the last gesture time for cooldown tracking"""
        current_time = time.time()
        
        if hand_id not in self.last_gesture_events:
            self.last_gesture_events[hand_id] = {}
        
        self.last_gesture_events[hand_id][gesture_type] = current_time
    
    def get_performance_stats(self) -> Dict:
        """Get performance statistics"""
        return {
            'tracked_states': len(self.hand_zone_states),
            'active_intersections': len(self.active_intersections),
            'detection_method': self.detection_method,
            'confidence_threshold': self.confidence_threshold
        }