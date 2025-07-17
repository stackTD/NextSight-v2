"""
Zone overlay widget for visual zone rendering in NextSight v2
Professional zone visualization with color coding and labels
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QRect, pyqtSignal
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QFontMetrics
from typing import List, Dict, Optional, Tuple
from nextsight.zones.zone_config import Zone, ZoneType


class ZoneOverlay(QWidget):
    """Overlay widget for rendering zones on top of camera feed"""
    
    # Signals
    zone_clicked = pyqtSignal(str)  # zone_id
    zone_hovered = pyqtSignal(str)  # zone_id
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Make widget transparent for overlay
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setStyleSheet("background: transparent;")
        
        # Zone data
        self.zones: List[Zone] = []
        self.zone_intersections: Dict[str, List[Dict]] = {}
        self.preview_zone: Optional[Dict] = None
        
        # Visual settings
        self.show_labels = True
        self.show_statistics = True
        self.show_intersections = True
        self.label_font_size = 10
        self.statistics_font_size = 8
        
        # Interaction state
        self.hovered_zone_id: Optional[str] = None
        self.selected_zone_id: Optional[str] = None
        
        # Animation settings
        self.blink_active_zones = True
        self.blink_timer_count = 0
        
        # Frame dimensions for coordinate conversion
        self.frame_width = 640
        self.frame_height = 480
    
    def set_frame_size(self, width: int, height: int):
        """Set frame dimensions for coordinate conversion"""
        self.frame_width = width
        self.frame_height = height
        self.update()
    
    def set_zones(self, zones: List[Zone]):
        """Update zones to display"""
        self.zones = zones.copy()
        self.update()
    
    def set_zone_intersections(self, intersections: Dict[str, List[Dict]]):
        """Update zone intersection data"""
        self.zone_intersections = intersections.copy()
        self.update()
    
    def set_preview_zone(self, preview_data: Optional[Dict]):
        """Set zone creation preview"""
        self.preview_zone = preview_data
        self.update()
    
    def set_visual_settings(self, show_labels: bool = None, show_statistics: bool = None,
                          show_intersections: bool = None, blink_active: bool = None):
        """Configure visual display settings"""
        if show_labels is not None:
            self.show_labels = show_labels
        if show_statistics is not None:
            self.show_statistics = show_statistics
        if show_intersections is not None:
            self.show_intersections = show_intersections
        if blink_active is not None:
            self.blink_active_zones = blink_active
        self.update()
    
    def paintEvent(self, event):
        """Paint zones and overlays"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        try:
            # Draw existing zones
            for zone in self.zones:
                if zone.active:
                    self._draw_zone(painter, zone)
            
            # Draw zone creation preview
            if self.preview_zone:
                self._draw_preview_zone(painter, self.preview_zone)
            
            # Draw zone statistics overlay
            if self.show_statistics and self.zones:
                self._draw_statistics_overlay(painter)
        
        except Exception as e:
            print(f"Error painting zone overlay: {e}")
        
        finally:
            painter.end()
    
    def _draw_zone(self, painter: QPainter, zone: Zone):
        """Draw individual zone with styling"""
        # Convert normalized coordinates to widget coordinates
        widget_rect = self._zone_to_widget_rect(zone)
        if not widget_rect:
            return
        
        # Determine zone state
        has_hands = zone.id in self.zone_intersections and self.zone_intersections[zone.id]
        is_hovered = zone.id == self.hovered_zone_id
        is_selected = zone.id == self.selected_zone_id
        
        # Get base color
        base_color = zone.get_color()
        
        # Modify color based on state
        if has_hands:
            # Brighter when hands are detected
            base_color = base_color.lighter(150)
            
            # Blink effect for active zones
            if self.blink_active_zones:
                blink_alpha = int(155 + 100 * abs(self.blink_timer_count % 60 - 30) / 30)
                base_color.setAlpha(blink_alpha)
            else:
                base_color.setAlpha(int(zone.alpha * 255 * 1.5))
        else:
            base_color.setAlpha(int(zone.alpha * 255))
        
        # Adjust for hover/selection
        if is_hovered:
            base_color = base_color.lighter(120)
        if is_selected:
            border_width = zone.border_width + 2
        else:
            border_width = zone.border_width
        
        # Draw zone rectangle
        painter.setPen(QPen(base_color.darker(120), border_width))
        painter.setBrush(QBrush(base_color))
        painter.drawRect(widget_rect)
        
        # Draw zone label
        if self.show_labels:
            self._draw_zone_label(painter, zone, widget_rect, has_hands)
        
        # Draw intersection indicators
        if self.show_intersections and has_hands:
            self._draw_intersection_indicators(painter, zone, widget_rect)
    
    def _draw_zone_label(self, painter: QPainter, zone: Zone, widget_rect: QRect, has_hands: bool):
        """Draw zone label and information"""
        # Setup label font
        label_font = QFont("Arial", self.label_font_size, QFont.Weight.Bold)
        painter.setFont(label_font)
        
        # Label text
        label_text = zone.name
        if has_hands:
            hand_count = len(self.zone_intersections.get(zone.id, []))
            label_text += f" ({hand_count} hand{'s' if hand_count != 1 else ''})"
        
        # Label background
        fm = QFontMetrics(label_font)
        text_rect = fm.boundingRect(label_text)
        label_rect = QRect(
            widget_rect.x() + 5,
            widget_rect.y() + 5,
            text_rect.width() + 10,
            text_rect.height() + 6
        )
        
        # Draw label background
        bg_color = QColor("#000000")
        bg_color.setAlpha(180)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(bg_color))
        painter.drawRoundedRect(label_rect, 3, 3)
        
        # Draw label text
        text_color = QColor("#ffffff")
        if zone.zone_type == ZoneType.PICK:
            text_color = QColor("#00ff00")
        elif zone.zone_type == ZoneType.DROP:
            text_color = QColor("#0080ff")
        
        painter.setPen(QPen(text_color))
        painter.drawText(
            label_rect.x() + 5,
            label_rect.y() + text_rect.height() + 3,
            label_text
        )
        
        # Draw zone type indicator
        type_text = zone.zone_type.value.upper()
        type_font = QFont("Arial", self.label_font_size - 2, QFont.Weight.Normal)
        painter.setFont(type_font)
        painter.setPen(QPen(text_color.darker(150)))
        painter.drawText(
            widget_rect.x() + widget_rect.width() - 50,
            widget_rect.y() + 15,
            type_text
        )
    
    def _draw_intersection_indicators(self, painter: QPainter, zone: Zone, widget_rect: QRect):
        """Draw indicators for hand intersections"""
        if zone.id not in self.zone_intersections:
            return
        
        intersections = self.zone_intersections[zone.id]
        
        # Draw hand indicators along zone border
        indicator_size = 8
        y_offset = 25
        
        for i, intersection in enumerate(intersections):
            hand_id = intersection.get('hand_id', f'hand_{i}')
            confidence = intersection.get('confidence', 0.0)
            
            # Position indicator along top border
            x_pos = widget_rect.x() + 10 + (i * 20)
            y_pos = widget_rect.y() + y_offset
            
            # Color based on confidence
            if confidence > 0.8:
                indicator_color = QColor("#00ff00")  # Green for high confidence
            elif confidence > 0.6:
                indicator_color = QColor("#ffaa00")  # Orange for medium confidence
            else:
                indicator_color = QColor("#ff6666")  # Red for low confidence
            
            # Draw indicator circle
            painter.setPen(QPen(indicator_color.darker(), 2))
            painter.setBrush(QBrush(indicator_color))
            painter.drawEllipse(x_pos, y_pos, indicator_size, indicator_size)
            
            # Draw hand ID label
            if len(hand_id) > 0:
                painter.setPen(QPen(QColor("#ffffff")))
                painter.setFont(QFont("Arial", 6))
                painter.drawText(x_pos - 5, y_pos + indicator_size + 10, hand_id[:1].upper())
    
    def _draw_preview_zone(self, painter: QPainter, preview_data: Dict):
        """Draw zone creation preview"""
        # Convert frame coordinates to widget coordinates
        widget_rect = self._frame_to_widget_rect(
            preview_data['x'], preview_data['y'],
            preview_data['width'], preview_data['height']
        )
        
        if not widget_rect:
            return
        
        # Preview styling
        preview_color = preview_data['color']
        preview_color.setAlpha(preview_data['alpha'])
        
        # Draw dashed border for preview
        pen = QPen(preview_color.darker(), preview_data['border_width'])
        pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.setBrush(QBrush(preview_color))
        painter.drawRect(widget_rect)
        
        # Draw preview label
        zone_type = preview_data.get('zone_type', 'zone')
        label_text = f"Creating {zone_type.title()} Zone"
        
        painter.setFont(QFont("Arial", self.label_font_size, QFont.Weight.Bold))
        painter.setPen(QPen(QColor("#ffffff")))
        painter.drawText(
            widget_rect.x() + 5,
            widget_rect.y() - 5,
            label_text
        )
    
    def _draw_statistics_overlay(self, painter: QPainter):
        """Draw zone statistics overlay"""
        # Calculate statistics
        total_zones = len(self.zones)
        active_zones = len([z for z in self.zones if z.active])
        zones_with_hands = len(self.zone_intersections)
        total_hands = sum(len(hands) for hands in self.zone_intersections.values())
        
        # Statistics text
        stats_lines = [
            f"Zones: {active_zones}/{total_zones}",
            f"Active: {zones_with_hands}",
            f"Hands: {total_hands}"
        ]
        
        # Setup font
        stats_font = QFont("Arial", self.statistics_font_size)
        painter.setFont(stats_font)
        fm = QFontMetrics(stats_font)
        
        # Calculate overlay position (top-right corner)
        line_height = fm.height()
        max_width = max(fm.boundingRect(line).width() for line in stats_lines)
        
        overlay_rect = QRect(
            self.width() - max_width - 20,
            10,
            max_width + 10,
            len(stats_lines) * line_height + 10
        )
        
        # Draw background
        bg_color = QColor("#000000")
        bg_color.setAlpha(160)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(bg_color))
        painter.drawRoundedRect(overlay_rect, 5, 5)
        
        # Draw statistics text
        painter.setPen(QPen(QColor("#ffffff")))
        for i, line in enumerate(stats_lines):
            painter.drawText(
                overlay_rect.x() + 5,
                overlay_rect.y() + 15 + (i * line_height),
                line
            )
    
    def _zone_to_widget_rect(self, zone: Zone) -> Optional[QRect]:
        """Convert zone to widget rectangle coordinates"""
        return self._frame_to_widget_rect(
            zone.x * self.frame_width,
            zone.y * self.frame_height,
            zone.width * self.frame_width,
            zone.height * self.frame_height
        )
    
    def _frame_to_widget_rect(self, frame_x: float, frame_y: float,
                            frame_w: float, frame_h: float) -> Optional[QRect]:
        """Convert frame coordinates to widget rectangle"""
        if self.width() <= 0 or self.height() <= 0:
            return None
        
        # Calculate aspect ratios
        widget_ratio = self.width() / self.height()
        frame_ratio = self.frame_width / self.frame_height
        
        # Calculate actual frame display area within widget
        if widget_ratio > frame_ratio:
            # Widget is wider than frame
            display_height = self.height()
            display_width = int(display_height * frame_ratio)
            offset_x = (self.width() - display_width) // 2
            offset_y = 0
        else:
            # Widget is taller than frame
            display_width = self.width()
            display_height = int(display_width / frame_ratio)
            offset_x = 0
            offset_y = (self.height() - display_height) // 2
        
        # Convert coordinates
        widget_x = int((frame_x / self.frame_width) * display_width) + offset_x
        widget_y = int((frame_y / self.frame_height) * display_height) + offset_y
        widget_w = int((frame_w / self.frame_width) * display_width)
        widget_h = int((frame_h / self.frame_height) * display_height)
        
        return QRect(widget_x, widget_y, widget_w, widget_h)
    
    def mousePressEvent(self, event):
        """Handle mouse clicks on zones"""
        if event.button() == Qt.MouseButton.LeftButton:
            clicked_zone = self._get_zone_at_position(event.pos())
            if clicked_zone:
                self.selected_zone_id = clicked_zone.id
                self.zone_clicked.emit(clicked_zone.id)
                self.update()
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Handle mouse hover over zones"""
        hovered_zone = self._get_zone_at_position(event.pos())
        new_hovered_id = hovered_zone.id if hovered_zone else None
        
        if new_hovered_id != self.hovered_zone_id:
            self.hovered_zone_id = new_hovered_id
            if new_hovered_id:
                self.zone_hovered.emit(new_hovered_id)
            self.update()
        
        super().mouseMoveEvent(event)
    
    def _get_zone_at_position(self, pos) -> Optional[Zone]:
        """Get zone at mouse position"""
        for zone in self.zones:
            if not zone.active:
                continue
            
            widget_rect = self._zone_to_widget_rect(zone)
            if widget_rect and widget_rect.contains(pos):
                return zone
        
        return None
    
    def animate_step(self):
        """Step animation (call periodically for blink effect)"""
        self.blink_timer_count += 1
        if self.blink_active_zones:
            self.update()
    
    def clear_selection(self):
        """Clear zone selection"""
        self.selected_zone_id = None
        self.hovered_zone_id = None
        self.update()