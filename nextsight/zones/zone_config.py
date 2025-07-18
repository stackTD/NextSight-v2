"""
Zone configuration and data models for NextSight v2
"""

import json
from dataclasses import dataclass, asdict
from enum import Enum
from typing import List, Dict, Optional, Tuple
from PyQt6.QtCore import QRect
from PyQt6.QtGui import QColor


class ZoneType(Enum):
    """Zone types for pick and drop operations"""
    PICK = "pick"
    DROP = "drop"


@dataclass
class Zone:
    """Zone data model for interactive zones"""
    
    # Zone identification
    id: str
    name: str
    zone_type: ZoneType
    
    # Zone geometry (normalized coordinates 0-1)
    x: float
    y: float 
    width: float
    height: float
    
    # Zone properties
    active: bool = True
    confidence_threshold: float = 0.7
    
    # Visual properties
    color: str = "#00ff00"  # Default green for pick zones
    alpha: float = 0.3
    border_width: int = 2
    
    # Interaction state
    hands_inside: List[str] = None
    last_interaction: Optional[float] = None
    interaction_count: int = 0
    
    def __post_init__(self):
        """Initialize defaults after creation"""
        if self.hands_inside is None:
            self.hands_inside = []
            
        # Set default colors based on zone type
        if self.zone_type == ZoneType.PICK and self.color == "#00ff00":
            self.color = "#00ff00"  # Green for pick zones
        elif self.zone_type == ZoneType.DROP and self.color == "#00ff00":
            self.color = "#0080ff"  # Blue for drop zones
    
    def to_qrect(self, frame_width: int, frame_height: int) -> QRect:
        """Convert normalized coordinates to QRect for given frame size"""
        x = int(self.x * frame_width)
        y = int(self.y * frame_height)
        width = int(self.width * frame_width)
        height = int(self.height * frame_height)
        return QRect(x, y, width, height)
    
    def get_color(self) -> QColor:
        """Get QColor object for the zone"""
        return QColor(self.color)
    
    def contains_point(self, x: float, y: float) -> bool:
        """Check if normalized point is inside zone"""
        return (self.x <= x <= self.x + self.width and
                self.y <= y <= self.y + self.height)
    
    def add_hand(self, hand_id: str):
        """Add hand to zone interaction"""
        if hand_id not in self.hands_inside:
            self.hands_inside.append(hand_id)
            self.interaction_count += 1
    
    def remove_hand(self, hand_id: str):
        """Remove hand from zone interaction"""
        if hand_id in self.hands_inside:
            self.hands_inside.remove(hand_id)
    
    def to_dict(self) -> Dict:
        """Convert zone to dictionary for serialization"""
        data = asdict(self)
        data['zone_type'] = self.zone_type.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Zone':
        """Create zone from dictionary"""
        # Handle zone_type conversion
        if 'zone_type' in data:
            data['zone_type'] = ZoneType(data['zone_type'])
        
        # Handle missing fields
        for field in ['hands_inside', 'last_interaction', 'interaction_count']:
            if field not in data:
                if field == 'hands_inside':
                    data[field] = []
                elif field == 'interaction_count':
                    data[field] = 0
                else:
                    data[field] = None
        
        return cls(**data)


class ZoneConfig:
    """Configuration manager for zones"""
    
    def __init__(self, config_file: str = "zones.json"):
        self.config_file = config_file
        self.zones: List[Zone] = []
        
        # Default zone settings
        self.default_pick_color = "#00ff00"  # Green
        self.default_drop_color = "#0080ff"  # Blue
        self.default_alpha = 0.3
        self.default_border_width = 2
        self.default_confidence_threshold = 0.7
        
        # Initialize with empty zones for fresh session
        # Note: Previous behavior loaded existing zones, causing session persistence
        # Load is now manual via load_zones() method if needed
        self.zones = []
    
    def add_zone(self, zone: Zone) -> bool:
        """Add new zone to configuration"""
        # Check for ID conflicts
        if any(z.id == zone.id for z in self.zones):
            return False
        
        self.zones.append(zone)
        return True
    
    def remove_zone(self, zone_id: str) -> bool:
        """Remove zone by ID"""
        for i, zone in enumerate(self.zones):
            if zone.id == zone_id:
                del self.zones[i]
                return True
        return False
    
    def get_zone(self, zone_id: str) -> Optional[Zone]:
        """Get zone by ID"""
        for zone in self.zones:
            if zone.id == zone_id:
                return zone
        return None
    
    def get_zones_by_type(self, zone_type: ZoneType) -> List[Zone]:
        """Get all zones of specific type"""
        return [zone for zone in self.zones if zone.zone_type == zone_type]
    
    def get_active_zones(self) -> List[Zone]:
        """Get all active zones"""
        return [zone for zone in self.zones if zone.active]
    
    def create_zone(self, name: str, zone_type: ZoneType, 
                   x: float, y: float, width: float, height: float) -> Zone:
        """Create new zone with default settings"""
        zone_id = f"{zone_type.value}_{len(self.zones):03d}"
        
        # Set default color based on type
        color = (self.default_pick_color if zone_type == ZoneType.PICK 
                else self.default_drop_color)
        
        zone = Zone(
            id=zone_id,
            name=name,
            zone_type=zone_type,
            x=x, y=y, width=width, height=height,
            color=color,
            alpha=self.default_alpha,
            border_width=self.default_border_width,
            confidence_threshold=self.default_confidence_threshold
        )
        
        return zone
    
    def save_zones(self) -> bool:
        """Save zones to configuration file"""
        try:
            data = {
                'zones': [zone.to_dict() for zone in self.zones],
                'settings': {
                    'default_pick_color': self.default_pick_color,
                    'default_drop_color': self.default_drop_color,
                    'default_alpha': self.default_alpha,
                    'default_border_width': self.default_border_width,
                    'default_confidence_threshold': self.default_confidence_threshold
                }
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error saving zones: {e}")
            return False
    
    def load_zones(self) -> bool:
        """Load zones from configuration file"""
        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)
            
            # Load zones
            self.zones = []
            if 'zones' in data:
                for zone_data in data['zones']:
                    try:
                        zone = Zone.from_dict(zone_data)
                        self.zones.append(zone)
                    except Exception as e:
                        print(f"Error loading zone: {e}")
            
            # Load settings
            if 'settings' in data:
                settings = data['settings']
                self.default_pick_color = settings.get('default_pick_color', self.default_pick_color)
                self.default_drop_color = settings.get('default_drop_color', self.default_drop_color)
                self.default_alpha = settings.get('default_alpha', self.default_alpha)
                self.default_border_width = settings.get('default_border_width', self.default_border_width)
                self.default_confidence_threshold = settings.get('default_confidence_threshold', self.default_confidence_threshold)
            
            return True
            
        except FileNotFoundError:
            # No config file exists yet, use defaults
            self.zones = []
            return True
        except Exception as e:
            print(f"Error loading zones: {e}")
            return False
    
    def clear_zones(self):
        """Clear all zones"""
        self.zones = []
    
    def get_zone_statistics(self) -> Dict:
        """Get zone interaction statistics"""
        stats = {
            'total_zones': len(self.zones),
            'active_zones': len(self.get_active_zones()),
            'pick_zones': len(self.get_zones_by_type(ZoneType.PICK)),
            'drop_zones': len(self.get_zones_by_type(ZoneType.DROP)),
            'total_interactions': sum(zone.interaction_count for zone in self.zones),
            'zones_with_hands': len([zone for zone in self.zones if zone.hands_inside])
        }
        
        return stats