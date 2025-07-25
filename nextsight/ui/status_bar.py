"""
Status bar component for NextSight v2
Enhanced with zone status and pick/drop event tracking for Phase 3
"""

from PyQt6.QtWidgets import QStatusBar, QLabel, QProgressBar, QWidget, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QColor
import time


class StatusBar(QStatusBar):
    """Professional status bar with multiple information panels"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Status tracking
        self.is_camera_connected = False
        self.is_detection_active = False
        self.current_fps = 0.0
        self.hands_detected = 0
        
        # Zone status tracking
        self.zones_enabled = False
        self.zone_creation_mode = None
        self.total_zones = 0
        self.active_zones = 0
        self.zones_with_hands = 0
        self.pick_events_count = 0
        self.drop_events_count = 0
        self.last_pick_time = 0
        self.last_drop_time = 0
        
        # Process status tracking
        self.process_message = ""
        self.process_message_color = "white"
        self.process_message_timer = None
        
        self.setup_ui()
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_status)
        self.update_timer.start(1000)  # Update every second
    
    def setup_ui(self):
        """Setup status bar components"""
        # Main status message
        self.status_label = QLabel("Initializing NextSight v2...")
        self.status_label.setObjectName("statusLabel")
        self.addWidget(self.status_label)
        
        # Camera status indicator
        self.camera_status = QLabel("Camera: Disconnected")
        self.camera_status.setMinimumWidth(150)
        self.camera_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.addPermanentWidget(self.camera_status)
        
        # Detection status
        self.detection_status = QLabel("Detection: Inactive")
        self.detection_status.setMinimumWidth(130)
        self.detection_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.addPermanentWidget(self.detection_status)
        
        # Hands counter
        self.hands_counter = QLabel("Hands: 0")
        self.hands_counter.setMinimumWidth(80)
        self.hands_counter.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.addPermanentWidget(self.hands_counter)
        
        # FPS display
        self.fps_display = QLabel("FPS: 0.0")
        self.fps_display.setMinimumWidth(80)
        self.fps_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.addPermanentWidget(self.fps_display)
        
        # Zone status
        self.zone_status = QLabel("Zone System: DISABLED")
        self.zone_status.setMinimumWidth(160)
        self.zone_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.addPermanentWidget(self.zone_status)
        
        # Zone creation mode status
        self.zone_mode_status = QLabel("Ready")
        self.zone_mode_status.setMinimumWidth(120)
        self.zone_mode_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.addPermanentWidget(self.zone_mode_status)
        
        # Pick events counter
        self.pick_counter = QLabel("Picks: 0")
        self.pick_counter.setMinimumWidth(80)
        self.pick_counter.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.addPermanentWidget(self.pick_counter)
        
        # Drop events counter  
        self.drop_counter = QLabel("Drops: 0")
        self.drop_counter.setMinimumWidth(80)
        self.drop_counter.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.addPermanentWidget(self.drop_counter)
        
        # Hand interaction status
        self.hand_interaction_status = QLabel("No hand interaction")
        self.hand_interaction_status.setMinimumWidth(150)
        self.hand_interaction_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.addPermanentWidget(self.hand_interaction_status)
        
        # Process status (for process completion messages)
        self.process_status = QLabel("")
        self.process_status.setMinimumWidth(200)
        self.process_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.process_status.setStyleSheet("font-weight: bold;")
        self.addPermanentWidget(self.process_status)
        self.hand_interaction_status.setStyleSheet("color: #ffffff; font-weight: bold;")
        self.addPermanentWidget(self.hand_interaction_status)
        
        # Keyboard instructions panel
        self.keyboard_instructions = QLabel("Press F1 for help | Z: Toggle zones | 1: Create pick zone | 2: Create drop zone")
        self.keyboard_instructions.setMinimumWidth(400)
        self.keyboard_instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.keyboard_instructions.setStyleSheet("color: #66ccff; font-weight: bold; font-size: 9pt;")
        self.addPermanentWidget(self.keyboard_instructions)
        
        # Performance indicator
        self.performance_indicator = QLabel()
        self.performance_indicator.setMinimumWidth(20)
        self.performance_indicator.setMaximumWidth(20)
        self.addPermanentWidget(self.performance_indicator)
        
        self.update_indicators()
    
    def update_status(self):
        """Update status bar information"""
        self.update_indicators()
    
    def update_indicators(self):
        """Update visual indicators based on current status"""
        # Camera status
        if self.is_camera_connected:
            self.camera_status.setText("Camera: Connected")
            self.camera_status.setStyleSheet("color: #00ff00; font-weight: bold;")
        else:
            self.camera_status.setText("Camera: Disconnected")
            self.camera_status.setStyleSheet("color: #ff6b6b; font-weight: bold;")
        
        # Detection status
        if self.is_detection_active:
            self.detection_status.setText("Detection: Active")
            self.detection_status.setStyleSheet("color: #00ff00; font-weight: bold;")
        else:
            self.detection_status.setText("Detection: Inactive")
            self.detection_status.setStyleSheet("color: #ffaa00; font-weight: bold;")
        
        # Hands counter with color coding
        self.hands_counter.setText(f"Hands: {self.hands_detected}")
        if self.hands_detected > 0:
            self.hands_counter.setStyleSheet("color: #00ff00; font-weight: bold;")
        else:
            self.hands_counter.setStyleSheet("color: #ffffff; font-weight: bold;")
        
        # FPS display with performance color coding
        self.fps_display.setText(f"FPS: {self.current_fps:.1f}")
        if self.current_fps >= 25:
            color = "#00ff00"  # Green for good performance
        elif self.current_fps >= 15:
            color = "#ffaa00"  # Orange for medium performance
        else:
            color = "#ff6b6b"  # Red for poor performance
        
        self.fps_display.setStyleSheet(f"color: {color}; font-weight: bold;")
        
        # Zone status with color coding
        if self.zones_enabled:
            zone_text = f"Zone System: ENABLED ({self.active_zones}/{self.total_zones})"
            if self.zones_with_hands > 0:
                zone_text += f" | Active: {self.zones_with_hands}"
                self.zone_status.setStyleSheet("color: #00ff00; font-weight: bold;")
            else:
                self.zone_status.setStyleSheet("color: #00cc00; font-weight: bold;")
        else:
            zone_text = "Zone System: DISABLED"
            self.zone_status.setStyleSheet("color: #666666; font-weight: bold;")
        
        self.zone_status.setText(zone_text)
        
        # Zone creation mode status
        if self.zone_creation_mode:
            mode_text = f"Creating {self.zone_creation_mode.title()} Zone"
            self.zone_mode_status.setStyleSheet("color: #ffaa00; font-weight: bold;")
        else:
            mode_text = "Ready"
            self.zone_mode_status.setStyleSheet("color: #ffffff; font-weight: normal;")
        
        self.zone_mode_status.setText(mode_text)
        
        # Pick counter with recent activity indication
        pick_text = f"Picks: {self.pick_events_count}"
        if time.time() - self.last_pick_time < 3.0:  # Recent pick event
            self.pick_counter.setStyleSheet("color: #00ff00; font-weight: bold;")
            pick_text += " ✓"
        else:
            self.pick_counter.setStyleSheet("color: #ffffff; font-weight: bold;")
        self.pick_counter.setText(pick_text)
        
        # Drop counter with recent activity indication
        drop_text = f"Drops: {self.drop_events_count}"
        if time.time() - self.last_drop_time < 3.0:  # Recent drop event
            self.drop_counter.setStyleSheet("color: #0080ff; font-weight: bold;")
            drop_text += " ✓"
        else:
            self.drop_counter.setStyleSheet("color: #ffffff; font-weight: bold;")
        self.drop_counter.setText(drop_text)
        
        # Performance indicator (traffic light style)
        self.update_performance_indicator()
    
    def update_performance_indicator(self):
        """Update the performance indicator icon"""
        # Create a small colored circle based on performance
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Determine color based on overall system performance
        if self.is_camera_connected and self.current_fps >= 25:
            if self.zones_enabled and self.active_zones > 0:
                color = QColor("#00ff00")  # Green - excellent with zones
            else:
                color = QColor("#00cc00")  # Slightly dimmer green without zones
        elif self.is_camera_connected and self.current_fps >= 15:
            color = QColor("#ffaa00")  # Orange - good
        elif self.is_camera_connected:
            color = QColor("#ff6b6b")  # Red - poor
        else:
            color = QColor("#666666")  # Gray - disconnected
        
        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(2, 2, 12, 12)
        painter.end()
        
        self.performance_indicator.setPixmap(pixmap)
    
    def set_camera_status(self, connected: bool):
        """Update camera connection status"""
        self.is_camera_connected = connected
        if connected:
            self.showMessage("Camera connected successfully", 3000)
        else:
            self.showMessage("Camera disconnected", 3000)
        self.update_indicators()
    
    def set_detection_status(self, active: bool):
        """Update detection status"""
        self.is_detection_active = active
        if active:
            self.showMessage("Hand detection activated", 2000)
        else:
            self.showMessage("Hand detection deactivated", 2000)
        self.update_indicators()
    
    def update_fps(self, fps: float):
        """Update FPS display"""
        self.current_fps = fps
        self.update_indicators()
    
    def update_hands_count(self, count: int):
        """Update hands detected count"""
        self.hands_detected = count
        self.update_indicators()
    
    def show_status_message(self, message: str, timeout: int = 0):
        """Show a status message"""
        self.status_label.setText(message)
        if timeout > 0:
            QTimer.singleShot(timeout, lambda: self.status_label.setText("Ready"))
    
    def show_error_message(self, message: str):
        """Show an error message"""
        self.status_label.setText(f"Error: {message}")
        self.status_label.setObjectName("errorLabel")
        self.status_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")
        
        # Reset style after 5 seconds
        QTimer.singleShot(5000, self.reset_status_style)
    
    def reset_status_style(self):
        """Reset status label style to default"""
        self.status_label.setObjectName("statusLabel")
        self.status_label.setStyleSheet("color: #ffffff; font-weight: normal;")
        self.status_label.setText("Ready")
    
    def set_ready_state(self):
        """Set status bar to ready state"""
        self.status_label.setText("Ready")
        self.reset_status_style()
    
    def update_zone_status(self, zone_data: dict):
        """Update zone-related status information"""
        self.zones_enabled = zone_data.get('is_enabled', False)
        
        if 'zones' in zone_data:
            zones_info = zone_data['zones']
            self.total_zones = zones_info.get('total_zones', 0)
            self.active_zones = zones_info.get('active_zones', 0)
            self.zones_with_hands = zones_info.get('zones_with_hands', 0)
        
        # Update event counters
        session_stats = zone_data.get('session_stats', {})
        self.pick_events_count = session_stats.get('total_picks', 0)
        self.drop_events_count = session_stats.get('total_drops', 0)
        
        self.update_indicators()
        
    def set_zone_creation_mode(self, mode: str = None):
        """Set zone creation mode status"""
        self.zone_creation_mode = mode
        self.update_indicators()
        
    def set_zone_system_enabled(self, enabled: bool):
        """Set zone system enabled status"""
        self.zones_enabled = enabled
        if enabled:
            self.showMessage("Zone system enabled - Press Z to toggle, 1/2 to create zones, E to edit", 3000)
        else:
            self.showMessage("Zone system disabled", 2000)
        self.update_indicators()
    
    def set_zone_editing_enabled(self, enabled: bool):
        """Set zone editing mode status"""
        if enabled:
            self.showMessage("Zone editing ENABLED - Click zones to select and drag control points to resize", 4000)
        else:
            self.showMessage("Zone editing DISABLED", 2000)
        self.update_indicators()
    
    def on_pick_event(self, hand_id: str, zone_id: str):
        """Handle pick event"""
        self.last_pick_time = time.time()
        self.showMessage(f"✓ PICK: {hand_id} in {zone_id}", 2000)
        # Flash pick counter briefly
        self.pick_counter.setStyleSheet("color: #00ff00; font-weight: bold; background-color: rgba(0, 255, 0, 50);")
        QTimer.singleShot(1000, lambda: self.pick_counter.setStyleSheet("color: #00ff00; font-weight: bold;"))
        self.update_indicators()
    
    def on_drop_event(self, hand_id: str, zone_id: str):
        """Handle drop event"""
        self.last_drop_time = time.time()
        self.showMessage(f"✓ DROP: {hand_id} in {zone_id}", 2000)
        # Flash drop counter briefly
        self.drop_counter.setStyleSheet("color: #0080ff; font-weight: bold; background-color: rgba(0, 128, 255, 50);")
        QTimer.singleShot(1000, lambda: self.drop_counter.setStyleSheet("color: #0080ff; font-weight: bold;"))
        self.update_indicators()
    
    def show_zone_message(self, message: str, timeout: int = 3000):
        """Show zone-related status message"""
        self.show_status_message(f"Zone: {message}", timeout)
    
    def show_hand_interaction(self, interaction_type: str, zone_id: str = None):
        """Show hand interaction status"""
        if interaction_type == "detected":
            if zone_id:
                text = f"Hand Detected in {zone_id}"
                color = "#00ff00"
            else:
                text = "Hand Detected"
                color = "#00cc00"
        elif interaction_type == "pick":
            text = f"Pick Event in {zone_id}" if zone_id else "Pick Event"
            color = "#ff9900"
        elif interaction_type == "drop":
            text = f"Drop Event in {zone_id}" if zone_id else "Drop Event"
            color = "#00ccff"
        else:
            text = "No hand interaction"
            color = "#ffffff"
        
        self.hand_interaction_status.setText(text)
        self.hand_interaction_status.setStyleSheet(f"color: {color}; font-weight: bold;")
        
        # Auto-reset after 3 seconds for detected/pick/drop events
        if interaction_type in ["detected", "pick", "drop"]:
            QTimer.singleShot(3000, lambda: self.show_hand_interaction("none"))
    
    def show_process_message(self, message: str, color: str = "white", timeout: int = 5000):
        """Show process completion/error message"""
        self.process_message = message
        self.process_message_color = color
        
        # Set the text and color
        self.process_status.setText(message)
        
        if color == "green":
            self.process_status.setStyleSheet("color: #00ff00; font-weight: bold;")
        elif color == "red":
            self.process_status.setStyleSheet("color: #ff6b6b; font-weight: bold;")
        else:
            self.process_status.setStyleSheet("color: #ffffff; font-weight: bold;")
        
        # Clear message after timeout
        if self.process_message_timer:
            self.process_message_timer.stop()
        
        self.process_message_timer = QTimer()
        self.process_message_timer.timeout.connect(self.clear_process_message)
        self.process_message_timer.start(timeout)
    
    def clear_process_message(self):
        """Clear the process status message"""
        self.process_status.setText("")
        self.process_status.setStyleSheet("")
        if self.process_message_timer:
            self.process_message_timer.stop()
            self.process_message_timer = None
            QTimer.singleShot(3000, lambda: self.show_hand_interaction("none"))