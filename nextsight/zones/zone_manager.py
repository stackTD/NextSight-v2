"""
Zone Manager - Main coordinator for zone management system in NextSight v2
Manages zone creation, intersection detection, and state coordination
"""

from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from typing import List, Dict, Optional, Callable
import time
import logging

from nextsight.zones.zone_config import Zone, ZoneType, ZoneConfig
from nextsight.zones.zone_creator import ZoneCreator
from nextsight.zones.intersection_detector import IntersectionDetector


class ZoneManager(QObject):
    """Main coordinator for zone management system"""
    
    # Signals for zone events
    zone_created = pyqtSignal(object)  # Zone
    zone_deleted = pyqtSignal(str)     # zone_id
    zone_updated = pyqtSignal(object)  # Zone
    
    # Signals for intersection events
    hand_entered_zone = pyqtSignal(str, object, dict)  # hand_id, zone, intersection_data
    hand_exited_zone = pyqtSignal(str, object, float)  # hand_id, zone, duration
    
    # Signals for status updates
    zone_status_changed = pyqtSignal(dict)  # status_data
    pick_event_detected = pyqtSignal(str, str)  # hand_id, zone_id
    drop_event_detected = pyqtSignal(str, str)  # hand_id, zone_id
    
    def __init__(self, config_file: str = "zones.json"):
        super().__init__()
        
        # Initialize components
        self.config = ZoneConfig(config_file)
        self.creator = ZoneCreator()
        self.intersection_detector = IntersectionDetector()
        
        # State management
        self.is_enabled = True
        self.detection_active = False
        self.frame_width = 640
        self.frame_height = 480
        
        # Performance tracking
        self.last_detection_time = 0
        self.detection_fps = 0.0
        self.detection_times = []
        
        # Zone interaction tracking
        self.pick_events = []
        self.drop_events = []
        self.session_stats = {
            'session_start': time.time(),
            'total_picks': 0,
            'total_drops': 0,
            'zones_created': 0,
            'zones_deleted': 0
        }
        
        # Setup connections and timers
        self.setup_connections()
        self.setup_timers()
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("Zone Manager initialized")
    
    def setup_connections(self):
        """Setup signal connections between components"""
        # Zone creator connections
        self.creator.zone_creation_completed.connect(self.on_zone_created)
        self.creator.zone_creation_cancelled.connect(self.on_zone_creation_cancelled)
        
        # Intersection detector connections
        self.intersection_detector.set_event_callbacks(
            on_enter=self.on_hand_enter_zone,
            on_exit=self.on_hand_exit_zone
        )
    
    def setup_timers(self):
        """Setup periodic update timers"""
        # Status update timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_zone_status)
        self.status_timer.start(1000)  # Update every second
        
        # Performance monitoring timer
        self.perf_timer = QTimer()
        self.perf_timer.timeout.connect(self.update_performance_metrics)
        self.perf_timer.start(5000)  # Update every 5 seconds
    
    def set_frame_size(self, width: int, height: int):
        """Set frame dimensions for coordinate calculations"""
        self.frame_width = width
        self.frame_height = height
        self.logger.info(f"Frame size set to {width}x{height}")
    
    def enable_detection(self, enabled: bool = True):
        """Enable or disable zone detection"""
        self.is_enabled = enabled
        self.detection_active = enabled
        self.logger.info(f"Zone detection {'enabled' if enabled else 'disabled'}")
    
    def start_zone_creation(self, zone_type: str) -> bool:
        """Start interactive zone creation"""
        if not self.is_enabled:
            return False
        
        try:
            self.creator.start_zone_creation(zone_type, self.frame_width, self.frame_height)
            self.logger.info(f"Started creating {zone_type} zone")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start zone creation: {e}")
            return False
    
    def cancel_zone_creation(self):
        """Cancel current zone creation"""
        self.creator.cancel_zone_creation()
    
    def create_zone_direct(self, name: str, zone_type: ZoneType, 
                         x: float, y: float, width: float, height: float) -> Optional[Zone]:
        """Create zone directly without mouse interaction"""
        try:
            zone = self.config.create_zone(name, zone_type, x, y, width, height)
            
            if self.config.add_zone(zone):
                self.session_stats['zones_created'] += 1
                self.zone_created.emit(zone)
                self.save_configuration()
                self.logger.info(f"Created zone: {zone.name} ({zone.id})")
                return zone
            else:
                self.logger.error(f"Failed to add zone: {zone.id}")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to create zone: {e}")
            return None
    
    def delete_zone(self, zone_id: str) -> bool:
        """Delete zone by ID"""
        try:
            zone = self.config.get_zone(zone_id)
            if zone and self.config.remove_zone(zone_id):
                self.session_stats['zones_deleted'] += 1
                self.intersection_detector.reset_zone_states(zone_id)
                self.zone_deleted.emit(zone_id)
                self.save_configuration()
                self.logger.info(f"Deleted zone: {zone_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to delete zone {zone_id}: {e}")
            return False
    
    def update_zone(self, zone: Zone) -> bool:
        """Update existing zone"""
        try:
            existing_zone = self.config.get_zone(zone.id)
            if existing_zone:
                # Update zone in config
                for i, z in enumerate(self.config.zones):
                    if z.id == zone.id:
                        self.config.zones[i] = zone
                        break
                
                self.zone_updated.emit(zone)
                self.save_configuration()
                self.logger.info(f"Updated zone: {zone.id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to update zone {zone.id}: {e}")
            return False
    
    def get_zones(self, active_only: bool = False) -> List[Zone]:
        """Get all zones or only active zones"""
        if active_only:
            return self.config.get_active_zones()
        return self.config.zones.copy()
    
    def get_zone(self, zone_id: str) -> Optional[Zone]:
        """Get zone by ID"""
        return self.config.get_zone(zone_id)
    
    def get_zones_by_type(self, zone_type: ZoneType) -> List[Zone]:
        """Get zones by type"""
        return self.config.get_zones_by_type(zone_type)
    
    def process_frame_detections(self, detection_info: Dict) -> Dict:
        """Process frame with zone detection"""
        if not self.is_enabled or not self.detection_active:
            return {'intersections': {}, 'events': [], 'statistics': {}}
        
        start_time = time.time()
        
        try:
            # Get active zones
            active_zones = self.config.get_active_zones()
            
            # Run intersection detection
            results = self.intersection_detector.detect_intersections(active_zones, detection_info)
            
            # Process events for pick/drop detection
            self.process_interaction_events(results['events'])
            
            # Update performance metrics
            detection_time = time.time() - start_time
            self.detection_times.append(detection_time)
            if len(self.detection_times) > 30:
                self.detection_times.pop(0)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error processing frame detections: {e}")
            return {'intersections': {}, 'events': [], 'statistics': {}}
    
    def process_interaction_events(self, events: List[Dict]):
        """Process zone interaction events for pick/drop detection"""
        for event in events:
            try:
                if event['type'] == 'hand_enter_zone':
                    zone = self.config.get_zone(event['zone_id'])
                    if zone:
                        if zone.zone_type == ZoneType.PICK:
                            self.pick_events.append(event)
                            self.session_stats['total_picks'] += 1
                            self.pick_event_detected.emit(event['hand_id'], event['zone_id'])
                            self.logger.info(f"Pick event: {event['hand_id']} in {event['zone_id']}")
                        
                        elif zone.zone_type == ZoneType.DROP:
                            self.drop_events.append(event)
                            self.session_stats['total_drops'] += 1
                            self.drop_event_detected.emit(event['hand_id'], event['zone_id'])
                            self.logger.info(f"Drop event: {event['hand_id']} in {event['zone_id']}")
                
            except Exception as e:
                self.logger.error(f"Error processing interaction event: {e}")
    
    def on_zone_created(self, zone: Zone):
        """Handle zone creation completion"""
        try:
            if self.config.add_zone(zone):
                self.session_stats['zones_created'] += 1
                self.zone_created.emit(zone)
                self.save_configuration()
                self.logger.info(f"Zone created via mouse: {zone.name} ({zone.id})")
            else:
                self.logger.error(f"Failed to add created zone: {zone.id}")
        except Exception as e:
            self.logger.error(f"Error handling zone creation: {e}")
    
    def on_zone_creation_cancelled(self):
        """Handle zone creation cancellation"""
        self.logger.info("Zone creation cancelled")
    
    def on_hand_enter_zone(self, hand_id: str, zone: Zone, intersection_data: Dict):
        """Handle hand entering zone event"""
        self.hand_entered_zone.emit(hand_id, zone, intersection_data)
        self.logger.debug(f"Hand {hand_id} entered zone {zone.id}")
    
    def on_hand_exit_zone(self, hand_id: str, zone: Zone, duration: float):
        """Handle hand exiting zone event"""
        self.hand_exited_zone.emit(hand_id, zone, duration)
        self.logger.debug(f"Hand {hand_id} exited zone {zone.id} after {duration:.2f}s")
    
    def update_zone_status(self):
        """Update zone status for UI"""
        if not self.is_enabled:
            return
        
        try:
            # Collect zone statistics
            zone_stats = self.config.get_zone_statistics()
            intersection_stats = self.intersection_detector.get_performance_stats()
            
            # Recent events (last 10 seconds)
            recent_time = time.time() - 10
            recent_picks = len([e for e in self.pick_events if e['timestamp'] > recent_time])
            recent_drops = len([e for e in self.drop_events if e['timestamp'] > recent_time])
            
            status_data = {
                'zones': zone_stats,
                'intersections': intersection_stats,
                'recent_picks': recent_picks,
                'recent_drops': recent_drops,
                'session_stats': self.session_stats.copy(),
                'detection_fps': self.detection_fps,
                'is_enabled': self.is_enabled,
                'detection_active': self.detection_active
            }
            
            self.zone_status_changed.emit(status_data)
            
        except Exception as e:
            self.logger.error(f"Error updating zone status: {e}")
    
    def update_performance_metrics(self):
        """Update performance metrics"""
        if self.detection_times:
            avg_time = sum(self.detection_times) / len(self.detection_times)
            self.detection_fps = 1.0 / avg_time if avg_time > 0 else 0.0
        else:
            self.detection_fps = 0.0
    
    def get_zone_creator(self) -> ZoneCreator:
        """Get zone creator for UI integration"""
        return self.creator
    
    def get_intersection_detector(self) -> IntersectionDetector:
        """Get intersection detector for configuration"""
        return self.intersection_detector
    
    def save_configuration(self) -> bool:
        """Save zone configuration to file"""
        try:
            return self.config.save_zones()
        except Exception as e:
            self.logger.error(f"Failed to save zone configuration: {e}")
            return False
    
    def load_configuration(self) -> bool:
        """Load zone configuration from file"""
        try:
            success = self.config.load_zones()
            if success:
                self.logger.info(f"Loaded {len(self.config.zones)} zones from configuration")
            return success
        except Exception as e:
            self.logger.error(f"Failed to load zone configuration: {e}")
            return False
    
    def clear_all_zones(self) -> bool:
        """Clear all zones"""
        try:
            self.config.clear_zones()
            self.intersection_detector.reset_zone_states()
            self.pick_events.clear()
            self.drop_events.clear()
            self.save_configuration()
            self.logger.info("All zones cleared")
            return True
        except Exception as e:
            self.logger.error(f"Failed to clear zones: {e}")
            return False
    
    def get_session_statistics(self) -> Dict:
        """Get comprehensive session statistics"""
        session_duration = time.time() - self.session_stats['session_start']
        
        stats = self.session_stats.copy()
        stats.update({
            'session_duration': session_duration,
            'picks_per_minute': (stats['total_picks'] / session_duration * 60) if session_duration > 0 else 0,
            'drops_per_minute': (stats['total_drops'] / session_duration * 60) if session_duration > 0 else 0,
            'current_zones': len(self.config.zones),
            'active_zones': len(self.config.get_active_zones()),
            'detection_fps': self.detection_fps
        })
        
        return stats
    
    def reset_session_statistics(self):
        """Reset session statistics"""
        self.session_stats = {
            'session_start': time.time(),
            'total_picks': 0,
            'total_drops': 0,
            'zones_created': 0,
            'zones_deleted': 0
        }
        self.pick_events.clear()
        self.drop_events.clear()
        self.logger.info("Session statistics reset")
    
    def set_detection_settings(self, method: str = None, confidence: float = None):
        """Configure detection settings"""
        if method:
            self.intersection_detector.set_detection_method(method)
        if confidence is not None:
            self.intersection_detector.set_confidence_threshold(confidence)
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            self.status_timer.stop()
            self.perf_timer.stop()
            self.save_configuration()
            self.logger.info("Zone Manager cleanup completed")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")