"""
Main widget for NextSight v2 interface
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                             QPushButton, QLabel, QGroupBox, QSlider, QCheckBox,
                             QSpacerItem, QSizePolicy, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from nextsight.ui.camera_widget import CameraWidget
from nextsight.ui.control_panel import EnhancedControlPanel
from nextsight.utils.config import config


class MainWidget(QWidget):
    """Main interface widget containing camera display and enhanced controls"""
    
    # Signals for main window communication (backward compatibility)
    toggle_detection_requested = pyqtSignal()
    toggle_landmarks_requested = pyqtSignal()
    toggle_connections_requested = pyqtSignal()
    confidence_threshold_changed = pyqtSignal(float)
    camera_switch_requested = pyqtSignal(int)
    
    # New signals for Phase 2
    toggle_hand_detection_requested = pyqtSignal()
    toggle_pose_detection_requested = pyqtSignal()
    toggle_pose_landmarks_requested = pyqtSignal()
    toggle_gesture_recognition_requested = pyqtSignal()
    reset_detection_settings_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Control states (for backward compatibility)
        self.detection_enabled = True
        self.landmarks_enabled = True
        self.connections_enabled = True
        
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Setup the main user interface with enhanced control panel"""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)
        
        # Left side - Camera display (takes most space)
        self.camera_widget = CameraWidget()
        main_layout.addWidget(self.camera_widget, stretch=3)
        
        # Right side - Enhanced control panel
        self.control_panel = EnhancedControlPanel()
        main_layout.addWidget(self.control_panel, stretch=1)
        
        # Legacy camera controls (keeping for compatibility)
        camera_controls = self.create_camera_controls()
        main_layout.addWidget(camera_controls, stretch=0)
    
    def create_camera_controls(self) -> QWidget:
        """Create simplified camera controls widget"""
        widget = QWidget()
        widget.setMaximumWidth(100)
        layout = QVBoxLayout(widget)
        
        # Camera selection buttons (simplified)
        self.camera0_btn = QPushButton("Cam 0")
        self.camera0_btn.setObjectName("toggleButton")
        self.camera0_btn.setCheckable(True)
        self.camera0_btn.setChecked(True)
        layout.addWidget(self.camera0_btn)
        
        self.camera1_btn = QPushButton("Cam 1")
        self.camera1_btn.setObjectName("toggleButton")
        self.camera1_btn.setCheckable(True)
        layout.addWidget(self.camera1_btn)
        
        # Camera info
        self.camera_info = QLabel("Camera 0")
        self.camera_info.setStyleSheet("color: #00ff00; font-weight: bold; font-size: 9pt;")
        layout.addWidget(self.camera_info)
        
        layout.addStretch()
        return widget
    
    def setup_connections(self):
        """Setup signal connections"""
        # Enhanced control panel connections
        self.control_panel.toggle_hand_detection_requested.connect(self.on_hand_detection_toggle)
        self.control_panel.toggle_pose_detection_requested.connect(self.on_pose_detection_toggle)
        self.control_panel.toggle_landmarks_requested.connect(self.on_landmarks_toggle)
        self.control_panel.toggle_connections_requested.connect(self.on_connections_toggle)
        self.control_panel.toggle_pose_landmarks_requested.connect(self.on_pose_landmarks_toggle)
        self.control_panel.toggle_gesture_recognition_requested.connect(self.on_gesture_toggle)
        self.control_panel.confidence_threshold_changed.connect(self.on_confidence_changed)
        self.control_panel.reset_detection_settings_requested.connect(self.on_reset_settings)
        
        # Camera buttons
        self.camera0_btn.clicked.connect(lambda: self.on_camera_switch(0))
        self.camera1_btn.clicked.connect(lambda: self.on_camera_switch(1))
    
    def on_hand_detection_toggle(self):
        """Handle hand detection toggle"""
        self.detection_enabled = not self.detection_enabled
        self.toggle_detection_requested.emit()  # For backward compatibility
        self.toggle_hand_detection_requested.emit()
    
    def on_pose_detection_toggle(self):
        """Handle pose detection toggle"""
        self.toggle_pose_detection_requested.emit()
    
    def on_landmarks_toggle(self, checked: bool = None):
        """Handle landmarks toggle"""
        if checked is not None:
            self.landmarks_enabled = checked
        else:
            self.landmarks_enabled = not self.landmarks_enabled
        self.toggle_landmarks_requested.emit()
    
    def on_connections_toggle(self, checked: bool = None):
        """Handle connections toggle"""
        if checked is not None:
            self.connections_enabled = checked
        else:
            self.connections_enabled = not self.connections_enabled
        self.toggle_connections_requested.emit()
    
    def on_pose_landmarks_toggle(self):
        """Handle pose landmarks toggle"""
        self.toggle_pose_landmarks_requested.emit()
    
    def on_gesture_toggle(self):
        """Handle gesture recognition toggle"""
        self.toggle_gesture_recognition_requested.emit()
    
    def on_reset_settings(self):
        """Handle reset settings"""
        self.reset_detection_settings_requested.emit()
    
    def on_confidence_changed(self, confidence: float):
        """Handle confidence threshold change"""
        self.confidence_threshold_changed.emit(confidence)
    
    def on_camera_switch(self, camera_index: int):
        """Handle camera switch"""
        # Update button states
        self.camera0_btn.setChecked(camera_index == 0)
        self.camera1_btn.setChecked(camera_index == 1)
        
        # Update info
        self.camera_info.setText(f"Cam {camera_index}")
        
        self.camera_switch_requested.emit(camera_index)
    
    # Backward compatibility methods for Phase 1 tests
    def on_detection_toggle(self):
        """Backward compatibility method for detection toggle"""
        self.on_hand_detection_toggle()
    
    def on_confidence_changed_int(self, value: int):
        """Handle confidence change from integer value (0-100)"""
        confidence = value / 100.0
        self.confidence_threshold_changed.emit(confidence)
    
    # Override the float version for compatibility
    def on_confidence_changed(self, value):
        """Handle confidence change - supports both int and float"""
        if isinstance(value, int):
            confidence = value / 100.0
        else:
            confidence = float(value)
        self.confidence_threshold_changed.emit(confidence)
    
    def update_fps_display(self, fps: float):
        """Update FPS in camera widget"""
        self.camera_widget.update_fps(fps)
    
    def update_detection_info(self, detection_info: dict):
        """Update detection information display"""
        # Update the enhanced control panel
        self.control_panel.update_detection_status(detection_info)
        
        # Update camera widget with detection info
        self.camera_widget.update_detection_info(detection_info)
    
    def get_camera_widget(self) -> CameraWidget:
        """Get reference to camera widget"""
        return self.camera_widget