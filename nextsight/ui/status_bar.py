"""
Status bar component for NextSight v2
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
            color = QColor("#00ff00")  # Green - excellent
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