"""
Zone Editor for interactive zone editing with control points
Implements drag-and-drop resizing and reshaping of zones
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QPoint, QRect, pyqtSignal
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QCursor, QMouseEvent
from typing import List, Dict, Optional, Tuple
from nextsight.zones.zone_config import Zone
import math


class ControlPoint:
    """Represents a control point for zone editing"""
    
    def __init__(self, x: float, y: float, point_type: str, zone_id: str):
        self.x = x  # Normalized coordinates (0-1)
        self.y = y
        self.point_type = point_type  # 'corner', 'edge', 'center'
        self.zone_id = zone_id
        self.size = 8  # Size in pixels
        self.hovered = False
        self.dragging = False
    
    def contains_point(self, x: float, y: float, widget_size: Tuple[int, int]) -> bool:
        """Check if a point is within this control point"""
        widget_x, widget_y = self._normalize_to_widget(widget_size)
        distance = math.sqrt((x - widget_x)**2 + (y - widget_y)**2)
        return distance <= self.size
    
    def _normalize_to_widget(self, widget_size: Tuple[int, int]) -> Tuple[float, float]:
        """Convert normalized coordinates to widget coordinates"""
        widget_width, widget_height = widget_size
        return self.x * widget_width, self.y * widget_height


class ZoneEditor(QWidget):
    """Interactive zone editor with control points for resizing/reshaping"""
    
    # Signals
    zone_modified = pyqtSignal(object)  # Zone object
    zone_selected = pyqtSignal(str)     # zone_id
    zone_deselected = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Make widget transparent for overlay but receive mouse events
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setStyleSheet("background: transparent;")
        
        # Enable mouse tracking for hover effects
        self.setMouseTracking(True)
        
        # Zone data
        self.zones: List[Zone] = []
        self.selected_zone_id: Optional[str] = None
        self.control_points: List[ControlPoint] = []
        
        # Editing state
        self.editing_enabled = False
        self.dragging_point: Optional[ControlPoint] = None
        self.drag_start_pos: Optional[QPoint] = None
        self.original_zone_bounds: Optional[Dict] = None
        
        # Visual settings
        self.control_point_color = QColor("#ffffff")
        self.control_point_border_color = QColor("#007ACC")
        self.control_point_hover_color = QColor("#00ff00")
        self.control_point_active_color = QColor("#ff8800")
        self.selection_border_color = QColor("#ffff00")
        self.selection_border_width = 3
        self.selection_border_dash_pattern = [5, 3]  # Dashed border pattern
        
        # Animation settings
        self.animation_timer = None
        self.animation_frame = 0
        
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
        self.zones = zones.copy() if zones else []
        self._update_control_points()
        self.update()
    
    def set_editing_enabled(self, enabled: bool):
        """Enable or disable zone editing"""
        self.editing_enabled = enabled
        if not enabled:
            self.selected_zone_id = None
            self.control_points.clear()
            self.zone_deselected.emit()
            if self.animation_timer:
                self.animation_timer.stop()
        else:
            self._update_control_points()
            # Start animation timer for visual effects
            if not self.animation_timer:
                from PyQt6.QtCore import QTimer
                self.animation_timer = QTimer()
                self.animation_timer.timeout.connect(self._animate)
            self.animation_timer.start(100)  # 10 FPS animation
        self.update()
    
    def select_zone(self, zone_id: str):
        """Select a zone for editing"""
        if not self.editing_enabled:
            return
        
        if zone_id != self.selected_zone_id:
            self.selected_zone_id = zone_id
            self._update_control_points()
            self.zone_selected.emit(zone_id)
            self.update()
    
    def deselect_zone(self):
        """Deselect the current zone"""
        if self.selected_zone_id:
            self.selected_zone_id = None
            self.control_points.clear()
            self.zone_deselected.emit()
            self.update()
    
    def _update_control_points(self):
        """Update control points for the selected zone"""
        self.control_points.clear()
        
        if not self.selected_zone_id or not self.editing_enabled:
            return
        
        # Find the selected zone
        selected_zone = None
        for zone in self.zones:
            if zone.id == self.selected_zone_id:
                selected_zone = zone
                break
        
        if not selected_zone:
            return
        
        # Create control points for zone boundaries
        x1, y1 = selected_zone.x, selected_zone.y
        x2, y2 = selected_zone.x + selected_zone.width, selected_zone.y + selected_zone.height
        
        # Corner control points
        self.control_points.extend([
            ControlPoint(x1, y1, 'corner_tl', selected_zone.id),  # Top-left
            ControlPoint(x2, y1, 'corner_tr', selected_zone.id),  # Top-right
            ControlPoint(x2, y2, 'corner_br', selected_zone.id),  # Bottom-right
            ControlPoint(x1, y2, 'corner_bl', selected_zone.id),  # Bottom-left
        ])
        
        # Edge midpoint control points
        mid_x, mid_y = x1 + selected_zone.width / 2, y1 + selected_zone.height / 2
        self.control_points.extend([
            ControlPoint(mid_x, y1, 'edge_top', selected_zone.id),     # Top edge
            ControlPoint(x2, mid_y, 'edge_right', selected_zone.id),   # Right edge
            ControlPoint(mid_x, y2, 'edge_bottom', selected_zone.id),  # Bottom edge
            ControlPoint(x1, mid_y, 'edge_left', selected_zone.id),    # Left edge
        ])
    
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press for control point interaction"""
        if not self.editing_enabled:
            return
        
        try:
            if event.button() == Qt.MouseButton.LeftButton:
                # Check if clicking on a control point
                click_pos = self._widget_to_normalized_coordinates(event.pos())
                if click_pos:
                    clicked_point = self._get_control_point_at_position(click_pos)
                    
                    if clicked_point:
                        # Start dragging control point
                        self.dragging_point = clicked_point
                        self.drag_start_pos = event.pos()
                        clicked_point.dragging = True
                        
                        # Store original zone bounds for constraint checking
                        selected_zone = self._get_selected_zone()
                        if selected_zone:
                            self.original_zone_bounds = {
                                'x': selected_zone.x,
                                'y': selected_zone.y,
                                'width': selected_zone.width,
                                'height': selected_zone.height
                            }
                        
                        self.setCursor(Qt.CursorShape.ClosedHandCursor)
                        self.update()
                        return
                    
                    # Check if clicking on a zone to select it
                    clicked_zone = self._get_zone_at_position(click_pos)
                    if clicked_zone:
                        self.select_zone(clicked_zone.id)
                    else:
                        self.deselect_zone()
        except Exception as e:
            print(f"Error in zone editor mouse press: {e}")
            # Reset state on error
            self.dragging_point = None
            self.drag_start_pos = None
            self.setCursor(Qt.CursorShape.ArrowCursor)
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move for dragging and hover effects"""
        if not self.editing_enabled:
            return
        
        try:
            # Update control point hover states
            mouse_pos = self._widget_to_normalized_coordinates(event.pos())
            if mouse_pos:
                hovered_point = self._get_control_point_at_position(mouse_pos)
                
                # Update hover states
                for point in self.control_points:
                    point.hovered = (point == hovered_point)
                
                # Set appropriate cursor
                if hovered_point:
                    self.setCursor(self._get_cursor_for_control_point(hovered_point))
                else:
                    self.setCursor(Qt.CursorShape.ArrowCursor)
            
            # Handle control point dragging
            if self.dragging_point and self.drag_start_pos:
                self._update_zone_from_drag(event.pos())
                self.update()
        except Exception as e:
            print(f"Error in zone editor mouse move: {e}")
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release to complete dragging"""
        if not self.editing_enabled:
            return
        
        try:
            if event.button() == Qt.MouseButton.LeftButton and self.dragging_point:
                # Complete the drag operation
                self.dragging_point.dragging = False
                self.dragging_point = None
                self.drag_start_pos = None
                self.original_zone_bounds = None
                
                # Emit zone modification signal
                selected_zone = self._get_selected_zone()
                if selected_zone:
                    self.zone_modified.emit(selected_zone)
                
                self.setCursor(Qt.CursorShape.ArrowCursor)
                self.update()
        except Exception as e:
            print(f"Error in zone editor mouse release: {e}")
            # Reset state on error
            if self.dragging_point:
                self.dragging_point.dragging = False
            self.dragging_point = None
            self.drag_start_pos = None
            self.original_zone_bounds = None
            self.setCursor(Qt.CursorShape.ArrowCursor)
    
    def _widget_to_normalized_coordinates(self, widget_pos: QPoint) -> Optional[Tuple[float, float]]:
        """Convert widget coordinates to normalized coordinates (0-1)"""
        widget_size = (self.width(), self.height())
        if widget_size[0] <= 0 or widget_size[1] <= 0:
            return None
        
        # Calculate aspect ratios
        widget_ratio = widget_size[0] / widget_size[1]
        frame_ratio = self.frame_width / self.frame_height
        
        # Calculate actual frame display area within widget
        if widget_ratio > frame_ratio:
            # Widget is wider than frame - frame is centered horizontally
            display_height = widget_size[1]
            display_width = int(display_height * frame_ratio)
            offset_x = (widget_size[0] - display_width) // 2
            offset_y = 0
        else:
            # Widget is taller than frame - frame is centered vertically
            display_width = widget_size[0]
            display_height = int(display_width / frame_ratio)
            offset_x = 0
            offset_y = (widget_size[1] - display_height) // 2
        
        # Check if point is within frame display area
        rel_x = widget_pos.x() - offset_x
        rel_y = widget_pos.y() - offset_y
        
        if 0 <= rel_x <= display_width and 0 <= rel_y <= display_height:
            # Convert to normalized coordinates
            norm_x = rel_x / display_width
            norm_y = rel_y / display_height
            return (norm_x, norm_y)
        
        return None
    
    def _normalized_to_widget_coordinates(self, norm_pos: Tuple[float, float]) -> Optional[Tuple[int, int]]:
        """Convert normalized coordinates to widget coordinates"""
        norm_x, norm_y = norm_pos
        widget_size = (self.width(), self.height())
        
        if widget_size[0] <= 0 or widget_size[1] <= 0:
            return None
        
        # Calculate aspect ratios and display area
        widget_ratio = widget_size[0] / widget_size[1]
        frame_ratio = self.frame_width / self.frame_height
        
        if widget_ratio > frame_ratio:
            display_height = widget_size[1]
            display_width = int(display_height * frame_ratio)
            offset_x = (widget_size[0] - display_width) // 2
            offset_y = 0
        else:
            display_width = widget_size[0]
            display_height = int(display_width / frame_ratio)
            offset_x = 0
            offset_y = (widget_size[1] - display_height) // 2
        
        # Convert to widget coordinates
        widget_x = int(norm_x * display_width) + offset_x
        widget_y = int(norm_y * display_height) + offset_y
        
        return (widget_x, widget_y)
    
    def _get_control_point_at_position(self, norm_pos: Tuple[float, float]) -> Optional[ControlPoint]:
        """Get control point at normalized position"""
        widget_pos = self._normalized_to_widget_coordinates(norm_pos)
        if not widget_pos:
            return None
        
        widget_size = (self.width(), self.height())
        
        for point in self.control_points:
            if point.contains_point(widget_pos[0], widget_pos[1], widget_size):
                return point
        
        return None
    
    def _get_zone_at_position(self, norm_pos: Tuple[float, float]) -> Optional[Zone]:
        """Get zone at normalized position"""
        norm_x, norm_y = norm_pos
        
        for zone in self.zones:
            if (zone.x <= norm_x <= zone.x + zone.width and 
                zone.y <= norm_y <= zone.y + zone.height):
                return zone
        
        return None
    
    def _get_selected_zone(self) -> Optional[Zone]:
        """Get the currently selected zone"""
        if not self.selected_zone_id:
            return None
        
        for zone in self.zones:
            if zone.id == self.selected_zone_id:
                return zone
        
        return None
    
    def _get_cursor_for_control_point(self, point: ControlPoint) -> Qt.CursorShape:
        """Get appropriate cursor for control point type"""
        if point.point_type.startswith('corner'):
            if point.point_type in ['corner_tl', 'corner_br']:
                return Qt.CursorShape.SizeFDiagCursor
            else:
                return Qt.CursorShape.SizeBDiagCursor
        elif point.point_type in ['edge_top', 'edge_bottom']:
            return Qt.CursorShape.SizeVerCursor
        elif point.point_type in ['edge_left', 'edge_right']:
            return Qt.CursorShape.SizeHorCursor
        else:
            return Qt.CursorShape.OpenHandCursor
    
    def _update_zone_from_drag(self, current_pos: QPoint):
        """Update zone bounds based on control point drag"""
        if not self.dragging_point or not self.drag_start_pos or not self.original_zone_bounds:
            return
        
        selected_zone = self._get_selected_zone()
        if not selected_zone:
            return
        
        # Calculate drag delta in normalized coordinates
        start_norm = self._widget_to_normalized_coordinates(self.drag_start_pos)
        current_norm = self._widget_to_normalized_coordinates(current_pos)
        
        if not start_norm or not current_norm:
            return
        
        delta_x = current_norm[0] - start_norm[0]
        delta_y = current_norm[1] - start_norm[1]
        
        # Update zone bounds based on control point type
        orig = self.original_zone_bounds
        point_type = self.dragging_point.point_type
        
        if point_type == 'corner_tl':
            # Top-left corner
            new_x = max(0, min(orig['x'] + delta_x, orig['x'] + orig['width'] - 0.05))
            new_y = max(0, min(orig['y'] + delta_y, orig['y'] + orig['height'] - 0.05))
            new_width = orig['width'] - (new_x - orig['x'])
            new_height = orig['height'] - (new_y - orig['y'])
        elif point_type == 'corner_tr':
            # Top-right corner
            new_x = orig['x']
            new_y = max(0, min(orig['y'] + delta_y, orig['y'] + orig['height'] - 0.05))
            new_width = max(0.05, min(1 - orig['x'], orig['width'] + delta_x))
            new_height = orig['height'] - (new_y - orig['y'])
        elif point_type == 'corner_br':
            # Bottom-right corner
            new_x = orig['x']
            new_y = orig['y']
            new_width = max(0.05, min(1 - orig['x'], orig['width'] + delta_x))
            new_height = max(0.05, min(1 - orig['y'], orig['height'] + delta_y))
        elif point_type == 'corner_bl':
            # Bottom-left corner
            new_x = max(0, min(orig['x'] + delta_x, orig['x'] + orig['width'] - 0.05))
            new_y = orig['y']
            new_width = orig['width'] - (new_x - orig['x'])
            new_height = max(0.05, min(1 - orig['y'], orig['height'] + delta_y))
        elif point_type == 'edge_top':
            # Top edge
            new_x = orig['x']
            new_y = max(0, min(orig['y'] + delta_y, orig['y'] + orig['height'] - 0.05))
            new_width = orig['width']
            new_height = orig['height'] - (new_y - orig['y'])
        elif point_type == 'edge_right':
            # Right edge
            new_x = orig['x']
            new_y = orig['y']
            new_width = max(0.05, min(1 - orig['x'], orig['width'] + delta_x))
            new_height = orig['height']
        elif point_type == 'edge_bottom':
            # Bottom edge
            new_x = orig['x']
            new_y = orig['y']
            new_width = orig['width']
            new_height = max(0.05, min(1 - orig['y'], orig['height'] + delta_y))
        elif point_type == 'edge_left':
            # Left edge
            new_x = max(0, min(orig['x'] + delta_x, orig['x'] + orig['width'] - 0.05))
            new_y = orig['y']
            new_width = orig['width'] - (new_x - orig['x'])
            new_height = orig['height']
        else:
            return
        
        # Apply constraints and update zone
        new_x = max(0, min(new_x, 1 - 0.05))
        new_y = max(0, min(new_y, 1 - 0.05))
        new_width = max(0.05, min(new_width, 1 - new_x))
        new_height = max(0.05, min(new_height, 1 - new_y))
        
        # Update zone bounds
        selected_zone.x = new_x
        selected_zone.y = new_y
        selected_zone.width = new_width
        selected_zone.height = new_height
        
        # Update control points
        self._update_control_points()
    
    def paintEvent(self, event):
        """Paint zone editor overlay"""
        if not self.editing_enabled:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        try:
            # Draw selection border for selected zone
            if self.selected_zone_id:
                selected_zone = self._get_selected_zone()
                if selected_zone:
                    self._draw_selection_border(painter, selected_zone)
            
            # Draw control points
            for point in self.control_points:
                self._draw_control_point(painter, point)
        
        except Exception as e:
            print(f"Error painting zone editor: {e}")
        
        finally:
            painter.end()
    
    def _draw_selection_border(self, painter: QPainter, zone: Zone):
        """Draw selection border around zone"""
        widget_rect = self._zone_to_widget_rect(zone)
        if not widget_rect:
            return
        
        # Animated dashed border
        pen = QPen(self.selection_border_color, self.selection_border_width)
        pen.setStyle(Qt.PenStyle.DashLine)
        
        # Animate dash offset for a "marching ants" effect
        dash_pattern = [6, 4]  # dash, space
        dash_offset = (self.animation_frame // 3) % (sum(dash_pattern))
        pen.setDashPattern(dash_pattern)
        pen.setDashOffset(dash_offset)
        
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        # Draw outer selection border
        rect = widget_rect
        painter.drawRect(rect[0] - 2, rect[1] - 2, rect[2] + 4, rect[3] + 4)
    
    def _draw_control_point(self, painter: QPainter, point: ControlPoint):
        """Draw a control point"""
        widget_pos = self._normalized_to_widget_coordinates((point.x, point.y))
        if not widget_pos:
            return
        
        x, y = widget_pos
        size = point.size
        
        # Choose colors based on state
        if point.dragging:
            fill_color = self.control_point_active_color
            border_color = self.control_point_border_color
            border_width = 3
        elif point.hovered:
            fill_color = self.control_point_hover_color
            border_color = self.control_point_border_color
            border_width = 2
            # Add slight glow effect for hovered points
            glow_size = size + 4
            glow_color = QColor(fill_color)
            glow_color.setAlpha(80)
            painter.setPen(QPen(glow_color, 1))
            painter.setBrush(QBrush(glow_color))
            painter.drawEllipse(x - glow_size//2, y - glow_size//2, glow_size, glow_size)
        else:
            fill_color = self.control_point_color
            border_color = self.control_point_border_color
            border_width = 2
        
        # Draw control point
        painter.setPen(QPen(border_color, border_width))
        painter.setBrush(QBrush(fill_color))
        
        # Draw different shapes for different point types
        if point.point_type.startswith('corner'):
            # Square for corners
            painter.drawRect(x - size//2, y - size//2, size, size)
            # Add small inner square for visual appeal
            inner_size = size - 4
            painter.setPen(QPen(border_color, 1))
            painter.drawRect(x - inner_size//2, y - inner_size//2, inner_size, inner_size)
        else:
            # Circle for edge midpoints
            painter.drawEllipse(x - size//2, y - size//2, size, size)
            # Add small inner circle
            inner_size = size - 4
            painter.setPen(QPen(border_color, 1))
            painter.drawEllipse(x - inner_size//2, y - inner_size//2, inner_size, inner_size)
    
    def _zone_to_widget_rect(self, zone: Zone) -> Optional[Tuple[int, int, int, int]]:
        """Convert zone normalized coordinates to widget rectangle"""
        top_left = self._normalized_to_widget_coordinates((zone.x, zone.y))
        bottom_right = self._normalized_to_widget_coordinates(
            (zone.x + zone.width, zone.y + zone.height)
        )
        
        if not top_left or not bottom_right:
            return None
        
        x, y = top_left
        width = bottom_right[0] - x
        height = bottom_right[1] - y
        
        return (x, y, width, height)
    
    def _animate(self):
        """Animation update for visual effects"""
        self.animation_frame = (self.animation_frame + 1) % 60
        if self.selected_zone_id or any(point.hovered for point in self.control_points):
            self.update()