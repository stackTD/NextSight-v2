"""
Interactive zone creation with mouse input for NextSight v2
Click and drag zone creation with visual preview
"""

from PyQt6.QtCore import QObject, pyqtSignal, QPoint
from PyQt6.QtGui import QMouseEvent, QPainter, QPen, QBrush, QColor
from typing import Optional, Tuple, Callable
from nextsight.zones.zone_config import Zone, ZoneType
from nextsight.utils.geometry import normalize_coordinates, create_zone_from_points
import time


class ZoneCreator(QObject):
    """Interactive zone creation with mouse input"""
    
    # Signals
    zone_creation_started = pyqtSignal(str)  # zone_type
    zone_creation_completed = pyqtSignal(object)  # Zone object
    zone_creation_cancelled = pyqtSignal()
    zone_preview_updated = pyqtSignal(object)  # Preview rectangle
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Creation state
        self.is_creating = False
        self.creation_mode = None  # 'pick' or 'drop'
        self.start_point: Optional[QPoint] = None
        self.current_point: Optional[QPoint] = None
        self.frame_width = 640
        self.frame_height = 480
        
        # Visual settings
        self.preview_colors = {
            ZoneType.PICK: QColor("#00ff00"),  # Green
            ZoneType.DROP: QColor("#0080ff")   # Blue
        }
        self.preview_alpha = 100
        self.preview_border_width = 2
        
        # Validation settings
        self.min_zone_size = 20  # Minimum size in pixels
        self.max_zone_ratio = 0.8  # Maximum zone size as ratio of frame
        
        # Zone naming
        self.zone_counter = {'pick': 0, 'drop': 0}
    
    def start_zone_creation(self, zone_type: str, frame_width: int, frame_height: int):
        """Start interactive zone creation"""
        if self.is_creating:
            self.cancel_zone_creation()
        
        self.creation_mode = zone_type.lower()
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.is_creating = True
        self.start_point = None
        self.current_point = None
        
        self.zone_creation_started.emit(zone_type)
    
    def cancel_zone_creation(self):
        """Cancel current zone creation"""
        if self.is_creating:
            self.is_creating = False
            self.creation_mode = None
            self.start_point = None
            self.current_point = None
            self.zone_creation_cancelled.emit()
    
    def handle_mouse_press(self, event: QMouseEvent, widget_size: Tuple[int, int]) -> bool:
        """Handle mouse press event during zone creation"""
        if not self.is_creating:
            return False
        
        if event.button() == Qt.MouseButton.LeftButton:
            # Convert widget coordinates to frame coordinates
            frame_point = self._widget_to_frame_coordinates(event.pos(), widget_size)
            if frame_point:
                self.start_point = frame_point
                self.current_point = frame_point
                return True
        
        elif event.button() == Qt.MouseButton.RightButton:
            # Cancel creation on right click
            self.cancel_zone_creation()
            return True
        
        return False
    
    def handle_mouse_move(self, event: QMouseEvent, widget_size: Tuple[int, int]) -> bool:
        """Handle mouse move event during zone creation"""
        if not self.is_creating or not self.start_point:
            return False
        
        # Convert widget coordinates to frame coordinates
        frame_point = self._widget_to_frame_coordinates(event.pos(), widget_size)
        if frame_point:
            self.current_point = frame_point
            
            # Emit preview update
            preview_rect = self._get_preview_rectangle()
            if preview_rect:
                self.zone_preview_updated.emit(preview_rect)
            else:
                # Clear preview if rectangle too small
                self.zone_preview_updated.emit(None)
            
            return True
        
        return False
    
    def handle_mouse_release(self, event: QMouseEvent, widget_size: Tuple[int, int]) -> bool:
        """Handle mouse release event during zone creation"""
        if not self.is_creating or not self.start_point:
            return False
        
        if event.button() == Qt.MouseButton.LeftButton:
            # Complete zone creation
            frame_point = self._widget_to_frame_coordinates(event.pos(), widget_size)
            if frame_point:
                self.current_point = frame_point
                zone = self._create_zone_from_points()
                
                if zone and self._validate_zone(zone):
                    self.zone_creation_completed.emit(zone)
                    self.is_creating = False
                    self.creation_mode = None
                    self.start_point = None
                    self.current_point = None
                    return True
                else:
                    # Invalid zone, keep creating
                    self.start_point = None
                    self.current_point = None
        
        return False
    
    def _widget_to_frame_coordinates(self, widget_pos: QPoint, 
                                   widget_size: Tuple[int, int]) -> Optional[QPoint]:
        """Convert widget coordinates to frame coordinates"""
        widget_width, widget_height = widget_size
        
        if widget_width <= 0 or widget_height <= 0:
            return None
        
        # Calculate aspect ratios
        widget_ratio = widget_width / widget_height
        frame_ratio = self.frame_width / self.frame_height
        
        # Calculate actual frame display area within widget (letterboxing/pillarboxing)
        if widget_ratio > frame_ratio:
            # Widget is wider than frame - frame is centered horizontally
            display_height = widget_height
            display_width = int(display_height * frame_ratio)
            offset_x = (widget_width - display_width) // 2
            offset_y = 0
        else:
            # Widget is taller than frame - frame is centered vertically  
            display_width = widget_width
            display_height = int(display_width / frame_ratio)
            offset_x = 0
            offset_y = (widget_height - display_height) // 2
        
        # Check if point is within frame display area
        rel_x = widget_pos.x() - offset_x
        rel_y = widget_pos.y() - offset_y
        
        if 0 <= rel_x <= display_width and 0 <= rel_y <= display_height:
            # Convert to frame coordinates (pixel coordinates)
            frame_x = int((rel_x / display_width) * self.frame_width)
            frame_y = int((rel_y / display_height) * self.frame_height)
            
            # Clamp to frame bounds
            frame_x = max(0, min(frame_x, self.frame_width - 1))
            frame_y = max(0, min(frame_y, self.frame_height - 1))
            
            return QPoint(frame_x, frame_y)
        
        return None
    
    def _get_preview_rectangle(self) -> Optional[dict]:
        """Get preview rectangle for current creation state"""
        if not self.start_point or not self.current_point:
            return None
        
        # Calculate rectangle bounds
        left = min(self.start_point.x(), self.current_point.x())
        top = min(self.start_point.y(), self.current_point.y())
        right = max(self.start_point.x(), self.current_point.x())
        bottom = max(self.start_point.y(), self.current_point.y())
        
        width = right - left
        height = bottom - top
        
        if width < self.min_zone_size or height < self.min_zone_size:
            return None
        
        # Get zone type for colors
        zone_type = ZoneType.PICK if self.creation_mode == 'pick' else ZoneType.DROP
        color = self.preview_colors[zone_type]
        
        return {
            'x': left / self.frame_width,      # Normalize to 0-1
            'y': top / self.frame_height,      # Normalize to 0-1
            'width': width / self.frame_width,  # Normalize to 0-1
            'height': height / self.frame_height, # Normalize to 0-1
            'color': color,
            'alpha': self.preview_alpha,
            'border_width': self.preview_border_width,
            'zone_type': zone_type.value
        }
    
    def _create_zone_from_points(self) -> Optional[Zone]:
        """Create zone from start and current points"""
        if not self.start_point or not self.current_point or not self.creation_mode:
            return None
        
        # Normalize coordinates
        start_norm = normalize_coordinates(
            self.start_point.x(), self.start_point.y(),
            self.frame_width, self.frame_height
        )
        end_norm = normalize_coordinates(
            self.current_point.x(), self.current_point.y(),
            self.frame_width, self.frame_height
        )
        
        # Create rectangle
        zone_rect = create_zone_from_points(start_norm, end_norm)
        
        # Determine zone type
        zone_type = ZoneType.PICK if self.creation_mode == 'pick' else ZoneType.DROP
        
        # Generate zone name
        self.zone_counter[self.creation_mode] += 1
        zone_name = f"{self.creation_mode.title()} Zone {self.zone_counter[self.creation_mode]}"
        
        # Create zone ID
        timestamp = int(time.time() * 1000) % 100000  # Last 5 digits of timestamp
        zone_id = f"{self.creation_mode}_{timestamp}"
        
        # Create zone
        zone = Zone(
            id=zone_id,
            name=zone_name,
            zone_type=zone_type,
            x=zone_rect.x,
            y=zone_rect.y,
            width=zone_rect.width,
            height=zone_rect.height,
            color=self.preview_colors[zone_type].name(),
            alpha=0.3,
            border_width=2
        )
        
        return zone
    
    def _validate_zone(self, zone: Zone) -> bool:
        """Validate zone size and position"""
        # Check minimum size
        pixel_width = zone.width * self.frame_width
        pixel_height = zone.height * self.frame_height
        
        if pixel_width < self.min_zone_size or pixel_height < self.min_zone_size:
            return False
        
        # Check maximum size
        if zone.width > self.max_zone_ratio or zone.height > self.max_zone_ratio:
            return False
        
        # Check bounds
        if (zone.x < 0 or zone.y < 0 or 
            zone.x + zone.width > 1.0 or 
            zone.y + zone.height > 1.0):
            return False
        
        return True
    
    def set_preview_colors(self, pick_color: QColor, drop_color: QColor):
        """Set preview colors for zone types"""
        self.preview_colors[ZoneType.PICK] = pick_color
        self.preview_colors[ZoneType.DROP] = drop_color
    
    def set_validation_settings(self, min_size: int = None, max_ratio: float = None):
        """Set zone validation settings"""
        if min_size is not None:
            self.min_zone_size = max(10, min_size)
        if max_ratio is not None:
            self.max_zone_ratio = max(0.1, min(1.0, max_ratio))
    
    def get_creation_status(self) -> dict:
        """Get current creation status"""
        return {
            'is_creating': self.is_creating,
            'creation_mode': self.creation_mode,
            'has_start_point': self.start_point is not None,
            'has_current_point': self.current_point is not None,
            'zone_counts': self.zone_counter.copy()
        }
    
    def draw_preview(self, painter: QPainter, widget_size: Tuple[int, int]):
        """Draw zone creation preview on painter"""
        if not self.is_creating or not self.start_point or not self.current_point:
            return
        
        preview_rect = self._get_preview_rectangle()
        if not preview_rect:
            return
        
        # Convert frame coordinates back to widget coordinates
        widget_rect = self._frame_to_widget_rectangle(
            preview_rect['x'], preview_rect['y'],
            preview_rect['width'], preview_rect['height'],
            widget_size
        )
        
        if not widget_rect:
            return
        
        # Setup painter
        color = preview_rect['color']
        color.setAlpha(preview_rect['alpha'])
        
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(color, preview_rect['border_width']))
        painter.setBrush(QBrush(color))
        
        # Draw rectangle
        painter.drawRect(*widget_rect)
        
        # Draw zone type label
        label_text = f"{preview_rect['zone_type'].title()} Zone"
        painter.setPen(QPen(QColor("#ffffff"), 1))
        painter.drawText(widget_rect[0] + 5, widget_rect[1] + 20, label_text)
    
    def _frame_to_widget_rectangle(self, frame_x: int, frame_y: int,
                                 frame_width: int, frame_height: int,
                                 widget_size: Tuple[int, int]) -> Optional[Tuple[int, int, int, int]]:
        """Convert frame rectangle to widget coordinates"""
        widget_width, widget_height = widget_size
        
        if widget_width <= 0 or widget_height <= 0:
            return None
        
        # Calculate aspect ratios and display area (same as _widget_to_frame_coordinates)
        widget_ratio = widget_width / widget_height
        frame_ratio = self.frame_width / self.frame_height
        
        if widget_ratio > frame_ratio:
            display_height = widget_height
            display_width = int(display_height * frame_ratio)
            offset_x = (widget_width - display_width) // 2
            offset_y = 0
        else:
            display_width = widget_width
            display_height = int(display_width / frame_ratio)
            offset_x = 0
            offset_y = (widget_height - display_height) // 2
        
        # Convert to widget coordinates
        widget_x = int((frame_x / self.frame_width) * display_width) + offset_x
        widget_y = int((frame_y / self.frame_height) * display_height) + offset_y
        widget_w = int((frame_width / self.frame_width) * display_width)
        widget_h = int((frame_height / self.frame_height) * display_height)
        
        return (widget_x, widget_y, widget_w, widget_h)