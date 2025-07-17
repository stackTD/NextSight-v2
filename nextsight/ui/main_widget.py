"""
Main widget for NextSight v2 interface
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                             QPushButton, QLabel, QGroupBox, QSlider, QCheckBox,
                             QSpacerItem, QSizePolicy, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from nextsight.ui.camera_widget import CameraWidget
from nextsight.utils.config import config


class MainWidget(QWidget):
    """Main interface widget containing camera display and controls"""
    
    # Signals for main window communication
    toggle_detection_requested = pyqtSignal()
    toggle_landmarks_requested = pyqtSignal()
    toggle_connections_requested = pyqtSignal()
    confidence_threshold_changed = pyqtSignal(float)
    camera_switch_requested = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Control states
        self.detection_enabled = True
        self.landmarks_enabled = True
        self.connections_enabled = True
        
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Setup the main user interface"""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)
        
        # Left side - Camera display (takes most space)
        self.camera_widget = CameraWidget()
        main_layout.addWidget(self.camera_widget, stretch=3)
        
        # Right side - Control panel
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel, stretch=1)
    
    def create_control_panel(self) -> QWidget:
        """Create the control panel with detection settings"""
        panel = QWidget()
        panel.setObjectName("controlPanel")
        panel.setMaximumWidth(300)
        panel.setMinimumWidth(250)
        
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        
        # Title
        title_label = QLabel("Detection Controls")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #007ACC; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background-color: #3e3e42;")
        layout.addWidget(separator)
        
        # Detection controls group
        detection_group = self.create_detection_group()
        layout.addWidget(detection_group)
        
        # Visualization controls group
        visualization_group = self.create_visualization_group()
        layout.addWidget(visualization_group)
        
        # Settings group
        settings_group = self.create_settings_group()
        layout.addWidget(settings_group)
        
        # Camera controls group
        camera_group = self.create_camera_group()
        layout.addWidget(camera_group)
        
        # Add stretch to push everything to top
        layout.addStretch()
        
        # Status info at bottom
        status_info = self.create_status_info()
        layout.addWidget(status_info)
        
        return panel
    
    def create_detection_group(self) -> QGroupBox:
        """Create detection control group"""
        group = QGroupBox("Hand Detection")
        layout = QVBoxLayout(group)
        
        # Main detection toggle
        self.detection_toggle = QPushButton("Disable Detection")
        self.detection_toggle.setObjectName("toggleButton")
        self.detection_toggle.setCheckable(True)
        self.detection_toggle.setChecked(True)
        layout.addWidget(self.detection_toggle)
        
        # Detection info
        self.detection_info = QLabel("Status: Active")
        self.detection_info.setStyleSheet("color: #00ff00; font-weight: bold;")
        layout.addWidget(self.detection_info)
        
        return group
    
    def create_visualization_group(self) -> QGroupBox:
        """Create visualization control group"""
        group = QGroupBox("Visualization")
        layout = QVBoxLayout(group)
        
        # Landmarks toggle
        self.landmarks_toggle = QCheckBox("Show Landmarks")
        self.landmarks_toggle.setChecked(True)
        layout.addWidget(self.landmarks_toggle)
        
        # Connections toggle
        self.connections_toggle = QCheckBox("Show Connections")
        self.connections_toggle.setChecked(True)
        layout.addWidget(self.connections_toggle)
        
        # Info overlay toggle
        self.overlay_toggle = QCheckBox("Show Info Overlay")
        self.overlay_toggle.setChecked(True)
        layout.addWidget(self.overlay_toggle)
        
        return group
    
    def create_settings_group(self) -> QGroupBox:
        """Create settings control group"""
        group = QGroupBox("Detection Settings")
        layout = QVBoxLayout(group)
        
        # Confidence threshold
        conf_label = QLabel("Confidence Threshold")
        layout.addWidget(conf_label)
        
        self.confidence_slider = QSlider(Qt.Orientation.Horizontal)
        self.confidence_slider.setMinimum(10)
        self.confidence_slider.setMaximum(100)
        self.confidence_slider.setValue(int(config.hand_detection.confidence_threshold * 100))
        self.confidence_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.confidence_slider.setTickInterval(10)
        layout.addWidget(self.confidence_slider)
        
        self.confidence_value = QLabel(f"{config.hand_detection.confidence_threshold:.2f}")
        self.confidence_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.confidence_value.setStyleSheet("font-weight: bold; color: #007ACC;")
        layout.addWidget(self.confidence_value)
        
        return group
    
    def create_camera_group(self) -> QGroupBox:
        """Create camera control group"""
        group = QGroupBox("Camera Controls")
        layout = QVBoxLayout(group)
        
        # Camera selection buttons
        camera_layout = QHBoxLayout()
        
        self.camera0_btn = QPushButton("Cam 0")
        self.camera0_btn.setObjectName("toggleButton")
        self.camera0_btn.setCheckable(True)
        self.camera0_btn.setChecked(True)
        camera_layout.addWidget(self.camera0_btn)
        
        self.camera1_btn = QPushButton("Cam 1")
        self.camera1_btn.setObjectName("toggleButton")
        self.camera1_btn.setCheckable(True)
        camera_layout.addWidget(self.camera1_btn)
        
        layout.addLayout(camera_layout)
        
        # Camera info
        self.camera_info = QLabel("Camera 0: Active")
        self.camera_info.setStyleSheet("color: #00ff00; font-weight: bold;")
        layout.addWidget(self.camera_info)
        
        return group
    
    def create_status_info(self) -> QWidget:
        """Create status information display"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Performance info
        self.performance_label = QLabel("Performance: Excellent")
        self.performance_label.setStyleSheet("color: #00ff00; font-weight: bold; font-size: 9pt;")
        layout.addWidget(self.performance_label)
        
        # Memory usage (placeholder for future)
        self.memory_label = QLabel("System: Ready")
        self.memory_label.setStyleSheet("color: #ffffff; font-size: 9pt;")
        layout.addWidget(self.memory_label)
        
        return widget
    
    def setup_connections(self):
        """Setup signal connections"""
        # Detection toggle
        self.detection_toggle.clicked.connect(self.on_detection_toggle)
        
        # Visualization toggles
        self.landmarks_toggle.toggled.connect(self.on_landmarks_toggle)
        self.connections_toggle.toggled.connect(self.on_connections_toggle)
        self.overlay_toggle.toggled.connect(self.on_overlay_toggle)
        
        # Confidence slider
        self.confidence_slider.valueChanged.connect(self.on_confidence_changed)
        
        # Camera buttons
        self.camera0_btn.clicked.connect(lambda: self.on_camera_switch(0))
        self.camera1_btn.clicked.connect(lambda: self.on_camera_switch(1))
    
    def on_detection_toggle(self):
        """Handle detection toggle"""
        self.detection_enabled = not self.detection_enabled
        
        if self.detection_enabled:
            self.detection_toggle.setText("Disable Detection")
            self.detection_info.setText("Status: Active")
            self.detection_info.setStyleSheet("color: #00ff00; font-weight: bold;")
        else:
            self.detection_toggle.setText("Enable Detection")
            self.detection_info.setText("Status: Inactive")
            self.detection_info.setStyleSheet("color: #ff6b6b; font-weight: bold;")
        
        self.toggle_detection_requested.emit()
    
    def on_landmarks_toggle(self, checked: bool):
        """Handle landmarks toggle"""
        self.landmarks_enabled = checked
        self.toggle_landmarks_requested.emit()
    
    def on_connections_toggle(self, checked: bool):
        """Handle connections toggle"""
        self.connections_enabled = checked
        self.toggle_connections_requested.emit()
    
    def on_overlay_toggle(self, checked: bool):
        """Handle overlay toggle"""
        self.camera_widget.toggle_info_overlay()
    
    def on_confidence_changed(self, value: int):
        """Handle confidence threshold change"""
        confidence = value / 100.0
        self.confidence_value.setText(f"{confidence:.2f}")
        self.confidence_threshold_changed.emit(confidence)
    
    def on_camera_switch(self, camera_index: int):
        """Handle camera switch"""
        # Update button states
        self.camera0_btn.setChecked(camera_index == 0)
        self.camera1_btn.setChecked(camera_index == 1)
        
        # Update info
        self.camera_info.setText(f"Camera {camera_index}: Active")
        
        self.camera_switch_requested.emit(camera_index)
    
    def update_fps_display(self, fps: float):
        """Update FPS in camera widget"""
        self.camera_widget.update_fps(fps)
        
        # Update performance indicator
        if fps >= 25:
            self.performance_label.setText("Performance: Excellent")
            self.performance_label.setStyleSheet("color: #00ff00; font-weight: bold; font-size: 9pt;")
        elif fps >= 15:
            self.performance_label.setText("Performance: Good")
            self.performance_label.setStyleSheet("color: #ffaa00; font-weight: bold; font-size: 9pt;")
        else:
            self.performance_label.setText("Performance: Poor")
            self.performance_label.setStyleSheet("color: #ff6b6b; font-weight: bold; font-size: 9pt;")
    
    def update_detection_info(self, detection_info: dict):
        """Update detection information display"""
        # Update status based on detection results
        hands_count = detection_info.get('hands_detected', 0)
        if hands_count > 0:
            self.memory_label.setText(f"Hands detected: {hands_count}")
            self.memory_label.setStyleSheet("color: #00ff00; font-size: 9pt;")
        else:
            self.memory_label.setText("No hands detected")
            self.memory_label.setStyleSheet("color: #ffffff; font-size: 9pt;")
    
    def get_camera_widget(self) -> CameraWidget:
        """Get reference to camera widget"""
        return self.camera_widget