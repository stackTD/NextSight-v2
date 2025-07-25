"""
Camera display widget for NextSight v2
Enhanced with zone overlay and mouse interaction for Phase 3
"""

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSizePolicy
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPointF
from PyQt6.QtGui import QPixmap, QImage, QPainter, QPen, QFont, QMouseEvent
from typing import Optional, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from nextsight.zones.zone_manager import ZoneManager
    from nextsight.ui.zone_overlay import ZoneOverlay
    from nextsight.ui.zone_editor import ZoneEditor


class CameraWidget(QWidget):
    """Professional camera display widget with zone overlay support"""
    
    # Signals
    clicked = pyqtSignal()
    zone_context_menu_requested = pyqtSignal()
    zone_editing_toggled = pyqtSignal(bool)  # New signal for zone editing mode
    zone_modified = pyqtSignal(object)        # New signal when zone is modified
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("cameraPanel")
        
        # Display properties
        self.current_image = None
        self.detection_info = {}
        self.show_info_overlay = True
        self.aspect_ratio = 16/9
        
        # Performance tracking
        self.fps_display = 0.0
        self.frame_count = 0
        
        # Zone system integration
        self.zone_manager: Optional['ZoneManager'] = None
        self.zone_overlay: Optional['ZoneOverlay'] = None
        self.zone_editor: Optional['ZoneEditor'] = None  # New zone editor
        self.zones_enabled = False
        self.zone_editing_enabled = False  # New editing mode flag
        
        # Zone creation variables
        self.zone_creation_mode = False
        self.creating_zone = False
        self.zone_start_point = (0.0, 0.0)
        self.zone_end_point = (0.0, 0.0)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the camera display UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Camera display label
        self.camera_label = QLabel()
        self.camera_label.setObjectName("cameraDisplay")
        self.camera_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera_label.setMinimumSize(640, 360)
        self.camera_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, 
            QSizePolicy.Policy.Expanding
        )
        self.camera_label.setScaledContents(False)
        
        # Set placeholder text
        self.camera_label.setText("Initializing Camera...")
        self.camera_label.setStyleSheet("""
            QLabel {
                border: 2px solid #007ACC;
                border-radius: 8px;
                background-color: #000000;
                color: #ffffff;
                font-size: 14pt;
                font-weight: bold;
            }
        """)
        
        # Info panel for detection stats
        self.info_label = QLabel()
        self.info_label.setObjectName("infoLabel")
        self.info_label.setMaximumHeight(80)
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("""
            QLabel {
                background-color: rgba(45, 45, 48, 200);
                border: 1px solid #3e3e42;
                border-radius: 6px;
                padding: 8px;
                color: #ffffff;
                font-size: 9pt;
            }
        """)
        
        layout.addWidget(self.camera_label)
        layout.addWidget(self.info_label)
        
        # Update info periodically
        self.info_timer = QTimer()
        self.info_timer.timeout.connect(self.update_info_display)
        self.info_timer.start(500)  # Update every 500ms
        
        # Zone overlay animation timer
        self.zone_animation_timer = QTimer()
        self.zone_animation_timer.timeout.connect(self.animate_zones)
        self.zone_animation_timer.start(50)  # 20 FPS for smooth animation
    
    def update_frame(self, qt_image: QImage, detection_info: Dict):
        """Update the camera display with new frame"""
        if qt_image.isNull():
            return
            
        self.current_image = qt_image
        self.detection_info = detection_info
        self.frame_count += 1
        
        # Scale image to fit widget while maintaining aspect ratio
        scaled_image = self.scale_image_to_fit(qt_image)
        
        # Add overlay if enabled
        if self.show_info_overlay:
            scaled_image = self.add_info_overlay(scaled_image)
        
        # Update display
        pixmap = QPixmap.fromImage(scaled_image)
        self.camera_label.setPixmap(pixmap)
        self.camera_label.setText("")  # Clear placeholder text
        
        # Update zone overlay and editor
        if self.zones_enabled:
            if self.zone_overlay:
                self.zone_overlay.set_frame_size(qt_image.width(), qt_image.height())
                self.zone_overlay.update()
            if self.zone_editor and self.zone_editing_enabled:
                self.zone_editor.set_frame_size(qt_image.width(), qt_image.height())
    
    def scale_image_to_fit(self, image: QImage) -> QImage:
        """Scale image to fit the widget while maintaining aspect ratio"""
        label_size = self.camera_label.size()
        
        if label_size.width() <= 0 or label_size.height() <= 0:
            return image
        
        # Calculate scaling to fit within widget
        scale_w = label_size.width() / image.width()
        scale_h = label_size.height() / image.height()
        scale = min(scale_w, scale_h)
        
        # Scale the image
        new_width = int(image.width() * scale)
        new_height = int(image.height() * scale)
        
        return image.scaled(
            new_width, new_height,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
    
    def add_info_overlay(self, image: QImage) -> QImage:
        """Add information overlay to the image"""
        if not self.detection_info:
            return image
        
        # Create a copy to draw on
        overlay_image = image.copy()
        painter = QPainter(overlay_image)
        
        # Setup painter
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw FPS counter
        fps_text = f"FPS: {self.fps_display:.1f}"
        painter.setPen(QPen(Qt.GlobalColor.green, 2))
        painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        painter.drawText(10, 25, fps_text)
        
        # Handle new detection info format
        y_offset = 50
        
        if 'hands' in self.detection_info:
            hands_info = self.detection_info['hands']
            hands_detected = hands_info.get('hands_detected', 0)
            hands_text = f"Hands: {hands_detected}"
            painter.setPen(QPen(Qt.GlobalColor.cyan, 2))
            painter.drawText(10, y_offset, hands_text)
            y_offset += 25
            
            # Draw handedness labels for new format
            if 'handedness' in hands_info and hands_info['handedness']:
                for hand_type in hands_info['handedness']:
                    painter.setPen(QPen(Qt.GlobalColor.yellow, 2))
                    painter.drawText(10, y_offset, f"• {hand_type}")
                    y_offset += 20
        else:
            # Backward compatibility with old format
            hands_detected = self.detection_info.get('hands_detected', 0)
            hands_text = f"Hands: {hands_detected}"
            painter.setPen(QPen(Qt.GlobalColor.cyan, 2))
            painter.drawText(10, y_offset, hands_text)
            y_offset += 25
            
            # Draw handedness labels for old format
            if 'handedness' in self.detection_info and self.detection_info['handedness']:
                for hand_type in self.detection_info['handedness']:
                    painter.setPen(QPen(Qt.GlobalColor.yellow, 2))
                    painter.drawText(10, y_offset, f"• {hand_type}")
                    y_offset += 20
        
        # Draw pose detection info
        if 'pose' in self.detection_info:
            pose_info = self.detection_info['pose']
            pose_detected = pose_info.get('pose_detected', False)
            pose_confidence = pose_info.get('pose_confidence', 0.0)
            
            pose_text = f"Pose: {'Yes' if pose_detected else 'No'}"
            if pose_detected:
                pose_text += f" ({pose_confidence:.2f})"
            
            painter.setPen(QPen(Qt.GlobalColor.magenta, 2))
            painter.drawText(10, y_offset, pose_text)
        
        painter.end()
        return overlay_image
    
    def update_detection_info(self, detection_info: dict):
        """Update detection information"""
        self.detection_info = detection_info
        # Update info display if it exists
        if hasattr(self, 'update_info_display'):
            self.update_info_display()
    
    def update_fps(self, fps: float):
        """Update FPS display"""
        self.fps_display = fps
    
    def update_info_display(self):
        """Update the information display panel"""
        if not self.detection_info:
            self.info_label.setText("Detection Info: No data available")
            return
        
        hands_count = self.detection_info.get('hands_detected', 0)
        handedness = self.detection_info.get('handedness', [])
        
        info_text = f"""
<b>Detection Status:</b><br>
• Hands detected: {hands_count}<br>
• Frame count: {self.frame_count}<br>
• FPS: {self.fps_display:.1f}<br>
        """.strip()
        
        if handedness:
            info_text += f"<br>• Hand types: {', '.join(handedness)}"
        
        self.info_label.setText(info_text)
    
    def toggle_info_overlay(self) -> bool:
        """Toggle the information overlay"""
        self.show_info_overlay = not self.show_info_overlay
        return self.show_info_overlay
    
    def toggle_info_panel(self) -> bool:
        """Toggle the information panel visibility"""
        visible = self.info_label.isVisible()
        self.info_label.setVisible(not visible)
        return not visible
    
    def set_placeholder_text(self, text: str):
        """Set placeholder text when no camera feed"""
        self.camera_label.clear()
        self.camera_label.setText(text)
    
    def clear_display(self):
        """Clear the camera display"""
        self.camera_label.clear()
        self.camera_label.setText("Camera Disconnected")
        self.detection_info = {}
        self.frame_count = 0
        self.fps_display = 0.0
    
    def mousePressEvent(self, event):
        """Handle mouse press events for zone creation and selection"""
        if not self.zone_creation_mode:
            # Forward to zone manager for zone selection
            if hasattr(self, 'zone_manager'):
                # Convert QPoint to QPointF for PyQt6 compatibility
                local_pos = QPointF(event.pos())
                global_pos = QPointF(event.globalPos())
                
                camera_event = QMouseEvent(
                    event.type(),
                    local_pos,  # Use QPointF instead of QPoint
                    global_pos,  # Use QPointF instead of QPoint
                    event.button(),
                    event.buttons(),
                    event.modifiers()
                )
                
                # Forward to zone manager
                self.zone_manager.mousePressEvent(camera_event)
            
            super().mousePressEvent(event)
            return
        
        # Zone creation logic
        if event.button() == Qt.MouseButton.LeftButton:
            # Convert to normalized coordinates
            widget_size = self.size()
            norm_x = event.pos().x() / widget_size.width()
            norm_y = event.pos().y() / widget_size.height()
            
            if not self.creating_zone:
                # Start creating zone
                self.creating_zone = True
                self.zone_start_point = (norm_x, norm_y)
                self.zone_end_point = (norm_x, norm_y)
                self.update()  # Trigger repaint
            else:
                # Finish creating zone
                self.zone_end_point = (norm_x, norm_y)
                self._finish_zone_creation()
        
        elif event.button() == Qt.MouseButton.RightButton:
            # Cancel zone creation
            if self.creating_zone:
                self.cancel_zone_creation()
    
    def resizeEvent(self, event):
        """Handle widget resize"""
        super().resizeEvent(event)
        # Update display if we have an image
        if self.current_image:
            self.update_frame(self.current_image, self.detection_info)
        
        # Resize zone overlay and editor to match camera label
        if self.zone_overlay:
            self.zone_overlay.setGeometry(self.camera_label.geometry())
        if self.zone_editor:
            self.zone_editor.setGeometry(self.camera_label.geometry())
    
    def set_zone_manager(self, zone_manager: 'ZoneManager'):
        """Set zone manager for zone functionality"""
        self.zone_manager = zone_manager
        
        # Create zone overlay
        if not self.zone_overlay:
            from nextsight.ui.zone_overlay import ZoneOverlay
            self.zone_overlay = ZoneOverlay(self)
            self.zone_overlay.setGeometry(self.camera_label.geometry())
            self.zone_overlay.zone_clicked.connect(self.on_zone_clicked)
            self.zone_overlay.zone_hovered.connect(self.on_zone_hovered)
        
        # Create zone editor
        if not self.zone_editor:
            from nextsight.ui.zone_editor import ZoneEditor
            self.zone_editor = ZoneEditor(self)
            self.zone_editor.setGeometry(self.camera_label.geometry())
            self.zone_editor.zone_modified.connect(self.on_zone_modified)
            self.zone_editor.zone_selected.connect(self.on_zone_selected_for_editing)
            self.zone_editor.zone_deselected.connect(self.on_zone_deselected_for_editing)
        
        # Connect zone manager signals
        if zone_manager:
            zone_manager.zone_created.connect(self.on_zones_updated)
            zone_manager.zone_deleted.connect(self.on_zone_deleted)
            zone_manager.zone_updated.connect(self.on_zones_updated)
            
            # Setup mouse interaction for zone creation
            zone_creator = zone_manager.get_zone_creator()
            zone_creator.zone_preview_updated.connect(self.on_zone_preview_updated)
            
            # Set frame size for coordinate calculations  
            zone_manager.set_frame_size(640, 480)  # Default size, will be updated by camera thread
        
        self.zones_enabled = True
    
    def enable_zones(self, enabled: bool = True):
        """Enable or disable zone display"""
        self.zones_enabled = enabled
        if self.zone_overlay:
            self.zone_overlay.setVisible(enabled)
        if self.zone_editor:
            self.zone_editor.setVisible(enabled and self.zone_editing_enabled)
    
    def update_zone_intersections(self, intersections: Dict):
        """Update zone intersection data"""
        if self.zone_overlay and self.zones_enabled:
            self.zone_overlay.set_zone_intersections(intersections)
    
    def on_zones_updated(self, *args):
        """Handle zone updates"""
        if self.zone_manager and self.zones_enabled:
            zones = self.zone_manager.get_zones(active_only=True)
            
            # Update zone overlay
            if self.zone_overlay:
                self.zone_overlay.set_zones(zones)
                self.zone_overlay.update()
            
            # Update zone editor
            if self.zone_editor and self.zone_editing_enabled:
                self.zone_editor.set_zones(zones)
    
    def on_zone_deleted(self, zone_id: str):
        """Handle zone deletion specifically"""
        if self.zone_manager and self.zones_enabled:
            # Clear any selection/hover state for the deleted zone in overlay
            if self.zone_overlay:
                if hasattr(self.zone_overlay, 'selected_zone_id') and self.zone_overlay.selected_zone_id == zone_id:
                    self.zone_overlay.selected_zone_id = None
                if hasattr(self.zone_overlay, 'hovered_zone_id') and self.zone_overlay.hovered_zone_id == zone_id:
                    self.zone_overlay.hovered_zone_id = None
            
            # Clear any selection state in zone editor
            if self.zone_editor and self.zone_editor.selected_zone_id == zone_id:
                self.zone_editor.deselect_zone()
            
            # Update zones list
            zones = self.zone_manager.get_zones(active_only=True)
            if self.zone_overlay:
                self.zone_overlay.set_zones(zones)
                self.zone_overlay.update()
            
            if self.zone_editor and self.zone_editing_enabled:
                self.zone_editor.set_zones(zones)
            
            # Force immediate visual refresh
            self.update()  # Update the camera widget too
    
    def on_zone_preview_updated(self, preview_data):
        """Handle zone creation preview updates"""
        if self.zone_overlay and self.zones_enabled:
            self.zone_overlay.set_preview_zone(preview_data)
    
    def on_zone_clicked(self, zone_id: str):
        """Handle zone click events"""
        if self.zone_manager:
            zone = self.zone_manager.get_zone(zone_id)
            if zone:
                print(f"Zone clicked: {zone.name} ({zone_id})")
    
    def on_zone_hovered(self, zone_id: str):
        """Handle zone hover events"""
        if self.zone_manager:
            zone = self.zone_manager.get_zone(zone_id)
            if zone:
                # Could show zone info in status bar
                pass
    
    def animate_zones(self):
        """Animate zone overlay effects"""
        if self.zone_overlay and self.zones_enabled:
            self.zone_overlay.animate_step()
    
    # Zone Editor Methods
    
    def set_zone_editing_enabled(self, enabled: bool):
        """Enable or disable zone editing mode"""
        self.zone_editing_enabled = enabled
        
        if self.zone_editor:
            self.zone_editor.set_editing_enabled(enabled)
            self.zone_editor.setVisible(enabled and self.zones_enabled)
            
            if enabled and self.zone_manager:
                # Update zone editor with current zones
                zones = self.zone_manager.get_zones()
                self.zone_editor.set_zones(zones)
        
        self.zone_editing_toggled.emit(enabled)
    
    def on_zone_modified(self, zone):
        """Handle zone modification from zone editor"""
        if self.zone_manager:
            # Update zone in zone manager
            self.zone_manager.update_zone(zone)
            
            # Update zone overlay
            zones = self.zone_manager.get_zones()
            if self.zone_overlay:
                self.zone_overlay.set_zones(zones)
        
        self.zone_modified.emit(zone)
    
    def on_zone_selected_for_editing(self, zone_id: str):
        """Handle zone selection for editing"""
        # Could add status updates or other feedback here
        pass
    
    def on_zone_deselected_for_editing(self):
        """Handle zone deselection for editing"""
        # Could add status updates or other feedback here
        pass
    
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press events for zone creation only"""
        if self.zone_manager and self.zones_enabled:
            zone_creator = self.zone_manager.get_zone_creator()
            
            # Get camera label position relative to the widget
            camera_pos = self.camera_label.mapFromParent(event.pos())
            widget_size = (self.camera_label.width(), self.camera_label.height())
            
            # Create new mouse event with camera label coordinates - use QPointF
            camera_event = QMouseEvent(
                event.type(),
                QPointF(camera_pos),  # Convert QPoint to QPointF
                event.globalPosition(),  # This is already QPointF in PyQt6
                event.button(),
                event.buttons(),
                event.modifiers()
            )
            
            if zone_creator.handle_mouse_press(camera_event, widget_size):
                return  # Event handled by zone creator
        
        # Default handling
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move events for zone creation"""
        if self.zone_manager and self.zones_enabled:
            zone_creator = self.zone_manager.get_zone_creator()
            
            # Get camera label position relative to the widget
            camera_pos = self.camera_label.mapFromParent(event.pos())
            widget_size = (self.camera_label.width(), self.camera_label.height())
            
            # Create new mouse event with camera label coordinates - use QPointF
            camera_event = QMouseEvent(
                event.type(),
                QPointF(camera_pos),  # Convert QPoint to QPointF
                event.globalPosition(),  # This is already QPointF in PyQt6
                event.button(),
                event.buttons(),
                event.modifiers()
            )
            
            if zone_creator.handle_mouse_move(camera_event, widget_size):
                return  # Event handled by zone creator
        
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release events for zone creation"""
        if self.zone_manager and self.zones_enabled:
            zone_creator = self.zone_manager.get_zone_creator()
            
            # Get camera label position relative to the widget
            camera_pos = self.camera_label.mapFromParent(event.pos())
            widget_size = (self.camera_label.width(), self.camera_label.height())
            
            # Create new mouse event with camera label coordinates - use QPointF
            camera_event = QMouseEvent(
                event.type(),
                QPointF(camera_pos),  # Convert QPoint to QPointF
                event.globalPosition(),  # This is already QPointF in PyQt6
                event.button(),
                event.buttons(),
                event.modifiers()
            )
            
            if zone_creator.handle_mouse_release(camera_event, widget_size):
                return  # Event handled by zone creator
        
        super().mouseReleaseEvent(event)