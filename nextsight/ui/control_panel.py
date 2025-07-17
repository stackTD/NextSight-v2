"""
Enhanced control panel for NextSight v2 Phase 2
Professional detection controls with keyboard shortcuts display
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                             QPushButton, QLabel, QGroupBox, QSlider, QCheckBox,
                             QSpacerItem, QSizePolicy, QFrame, QTextEdit)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from nextsight.utils.config import config
from nextsight.utils.detection_config import detection_config, get_keyboard_help
import logging


class EnhancedControlPanel(QWidget):
    """Enhanced control panel with professional detection controls"""
    
    # Signals for detection control
    toggle_hand_detection_requested = pyqtSignal()
    toggle_pose_detection_requested = pyqtSignal()
    toggle_landmarks_requested = pyqtSignal()
    toggle_connections_requested = pyqtSignal()
    toggle_pose_landmarks_requested = pyqtSignal()
    toggle_gesture_recognition_requested = pyqtSignal()
    confidence_threshold_changed = pyqtSignal(float)
    reset_detection_settings_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Control states
        self.hand_detection_enabled = True
        self.pose_detection_enabled = True
        self.landmarks_enabled = True
        self.connections_enabled = True
        self.pose_landmarks_enabled = True
        self.gesture_recognition_enabled = False
        
        self.logger = logging.getLogger(__name__)
        
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Setup the enhanced control panel UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)
        
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
        
        # Hand detection group
        hand_group = self.create_hand_detection_group()
        layout.addWidget(hand_group)
        
        # Pose detection group
        pose_group = self.create_pose_detection_group()
        layout.addWidget(pose_group)
        
        # Visualization controls
        viz_group = self.create_visualization_group()
        layout.addWidget(viz_group)
        
        # Settings group
        settings_group = self.create_settings_group()
        layout.addWidget(settings_group)
        
        # Keyboard shortcuts
        keyboard_group = self.create_keyboard_shortcuts_group()
        layout.addWidget(keyboard_group)
        
        # Reset button
        reset_btn = QPushButton("Reset All Settings (R)")
        reset_btn.setObjectName("resetButton")
        reset_btn.setStyleSheet("""
            QPushButton#resetButton {
                background-color: #ff6b6b;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton#resetButton:hover {
                background-color: #ff5252;
            }
            QPushButton#resetButton:pressed {
                background-color: #d32f2f;
            }
        """)
        reset_btn.clicked.connect(self.on_reset_settings)
        layout.addWidget(reset_btn)
        
        # Add stretch to push everything to top
        layout.addStretch()
    
    def create_hand_detection_group(self) -> QGroupBox:
        """Create hand detection control group"""
        group = QGroupBox("Hand Detection")
        layout = QVBoxLayout(group)
        
        # Main toggle
        self.hand_detection_toggle = QPushButton("Disable Hand Detection (H)")
        self.hand_detection_toggle.setObjectName("toggleButton")
        self.hand_detection_toggle.setCheckable(True)
        self.hand_detection_toggle.setChecked(True)
        layout.addWidget(self.hand_detection_toggle)
        
        # Gesture recognition toggle
        self.gesture_toggle = QPushButton("Enable Gesture Recognition (G)")
        self.gesture_toggle.setObjectName("toggleButton")
        self.gesture_toggle.setCheckable(True)
        layout.addWidget(self.gesture_toggle)
        
        # Hand status
        self.hand_status = QLabel("Status: Active")
        self.hand_status.setStyleSheet("color: #00ff00; font-weight: bold;")
        layout.addWidget(self.hand_status)
        
        return group
    
    def create_pose_detection_group(self) -> QGroupBox:
        """Create pose detection control group"""
        group = QGroupBox("Pose Detection")
        layout = QVBoxLayout(group)
        
        # Main toggle
        self.pose_detection_toggle = QPushButton("Disable Pose Detection (B)")
        self.pose_detection_toggle.setObjectName("toggleButton")
        self.pose_detection_toggle.setCheckable(True)
        self.pose_detection_toggle.setChecked(True)
        layout.addWidget(self.pose_detection_toggle)
        
        # Pose landmarks toggle
        self.pose_landmarks_toggle = QPushButton("Hide Pose Landmarks (P)")
        self.pose_landmarks_toggle.setObjectName("toggleButton")
        self.pose_landmarks_toggle.setCheckable(True)
        self.pose_landmarks_toggle.setChecked(True)
        layout.addWidget(self.pose_landmarks_toggle)
        
        # Pose status
        self.pose_status = QLabel("Status: Active")
        self.pose_status.setStyleSheet("color: #00ff00; font-weight: bold;")
        layout.addWidget(self.pose_status)
        
        return group
    
    def create_visualization_group(self) -> QGroupBox:
        """Create visualization control group"""
        group = QGroupBox("Visualization")
        layout = QVBoxLayout(group)
        
        # Landmarks toggle
        self.landmarks_toggle = QCheckBox("Show Hand Landmarks (L)")
        self.landmarks_toggle.setChecked(True)
        layout.addWidget(self.landmarks_toggle)
        
        # Connections toggle
        self.connections_toggle = QCheckBox("Show Hand Connections (C)")
        self.connections_toggle.setChecked(True)
        layout.addWidget(self.connections_toggle)
        
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
    
    def create_keyboard_shortcuts_group(self) -> QGroupBox:
        """Create keyboard shortcuts display group"""
        group = QGroupBox("Keyboard Shortcuts")
        layout = QVBoxLayout(group)
        
        # Create compact shortcuts display
        shortcuts_text = QTextEdit()
        shortcuts_text.setMaximumHeight(120)
        shortcuts_text.setReadOnly(True)
        shortcuts_text.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #3e3e42;
                font-family: 'Courier New', monospace;
                font-size: 9pt;
            }
        """)
        
        shortcuts_content = """H - Toggle Hand Detection
B - Toggle Pose Detection  
P - Toggle Pose Landmarks
Z - Toggle Zone Detection
1 - Create Pick zone
2 - Create Drop zone
C - Toggle Connections
R - Reset Settings
ESC - Exit Application"""
        
        shortcuts_text.setPlainText(shortcuts_content)
        layout.addWidget(shortcuts_text)
        
        return group
    
    def setup_connections(self):
        """Setup signal connections"""
        # Detection toggles
        self.hand_detection_toggle.clicked.connect(self.on_hand_detection_toggle)
        self.pose_detection_toggle.clicked.connect(self.on_pose_detection_toggle)
        self.pose_landmarks_toggle.clicked.connect(self.on_pose_landmarks_toggle)
        self.gesture_toggle.clicked.connect(self.on_gesture_toggle)
        
        # Visualization toggles
        self.landmarks_toggle.toggled.connect(self.on_landmarks_toggle)
        self.connections_toggle.toggled.connect(self.on_connections_toggle)
        
        # Confidence slider
        self.confidence_slider.valueChanged.connect(self.on_confidence_changed)
    
    def on_hand_detection_toggle(self):
        """Handle hand detection toggle"""
        self.hand_detection_enabled = not self.hand_detection_enabled
        
        if self.hand_detection_enabled:
            self.hand_detection_toggle.setText("Disable Hand Detection (H)")
            self.hand_status.setText("Status: Active")
            self.hand_status.setStyleSheet("color: #00ff00; font-weight: bold;")
        else:
            self.hand_detection_toggle.setText("Enable Hand Detection (H)")
            self.hand_status.setText("Status: Inactive")
            self.hand_status.setStyleSheet("color: #ff6b6b; font-weight: bold;")
        
        self.toggle_hand_detection_requested.emit()
    
    def on_pose_detection_toggle(self):
        """Handle pose detection toggle"""
        self.pose_detection_enabled = not self.pose_detection_enabled
        
        if self.pose_detection_enabled:
            self.pose_detection_toggle.setText("Disable Pose Detection (B)")
            self.pose_status.setText("Status: Active")
            self.pose_status.setStyleSheet("color: #00ff00; font-weight: bold;")
        else:
            self.pose_detection_toggle.setText("Enable Pose Detection (B)")
            self.pose_status.setText("Status: Inactive")
            self.pose_status.setStyleSheet("color: #ff6b6b; font-weight: bold;")
        
        self.toggle_pose_detection_requested.emit()
    
    def on_pose_landmarks_toggle(self):
        """Handle pose landmarks toggle"""
        self.pose_landmarks_enabled = not self.pose_landmarks_enabled
        
        if self.pose_landmarks_enabled:
            self.pose_landmarks_toggle.setText("Hide Pose Landmarks (P)")
        else:
            self.pose_landmarks_toggle.setText("Show Pose Landmarks (P)")
        
        self.toggle_pose_landmarks_requested.emit()
    
    def on_gesture_toggle(self):
        """Handle gesture recognition toggle"""
        self.gesture_recognition_enabled = not self.gesture_recognition_enabled
        
        if self.gesture_recognition_enabled:
            self.gesture_toggle.setText("Disable Gesture Recognition (G)")
        else:
            self.gesture_toggle.setText("Enable Gesture Recognition (G)")
        
        self.toggle_gesture_recognition_requested.emit()
    
    def on_landmarks_toggle(self, checked: bool):
        """Handle landmarks toggle"""
        self.landmarks_enabled = checked
        self.toggle_landmarks_requested.emit()
    
    def on_connections_toggle(self, checked: bool):
        """Handle connections toggle"""
        self.connections_enabled = checked
        self.toggle_connections_requested.emit()
    
    def on_confidence_changed(self, value: int):
        """Handle confidence threshold change"""
        confidence = value / 100.0
        self.confidence_value.setText(f"{confidence:.2f}")
        self.confidence_threshold_changed.emit(confidence)
    
    def on_reset_settings(self):
        """Handle reset settings button"""
        # Reset UI states
        self.hand_detection_enabled = True
        self.pose_detection_enabled = True
        self.landmarks_enabled = True
        self.connections_enabled = True
        self.pose_landmarks_enabled = True
        self.gesture_recognition_enabled = False
        
        # Update UI elements
        self.hand_detection_toggle.setChecked(True)
        self.hand_detection_toggle.setText("Disable Hand Detection (H)")
        self.hand_status.setText("Status: Active")
        self.hand_status.setStyleSheet("color: #00ff00; font-weight: bold;")
        
        self.pose_detection_toggle.setChecked(True)
        self.pose_detection_toggle.setText("Disable Pose Detection (B)")
        self.pose_status.setText("Status: Active")
        self.pose_status.setStyleSheet("color: #00ff00; font-weight: bold;")
        
        self.pose_landmarks_toggle.setChecked(True)
        self.pose_landmarks_toggle.setText("Hide Pose Landmarks (P)")
        
        self.gesture_toggle.setChecked(False)
        self.gesture_toggle.setText("Enable Gesture Recognition (G)")
        
        self.landmarks_toggle.setChecked(True)
        self.connections_toggle.setChecked(True)
        
        self.confidence_slider.setValue(50)
        self.confidence_value.setText("0.50")
        
        self.reset_detection_settings_requested.emit()
        self.logger.info("Control panel reset to defaults")
    
    def update_detection_status(self, detection_info: dict):
        """Update display with current detection status"""
        # Update based on detection info from camera thread
        if 'hands' in detection_info:
            hands_count = detection_info['hands'].get('hands_detected', 0)
            if hands_count > 0:
                self.hand_status.setText(f"Status: {hands_count} hand(s) detected")
            else:
                self.hand_status.setText("Status: Active (no hands)")
        
        if 'pose' in detection_info:
            pose_detected = detection_info['pose'].get('pose_detected', False)
            if pose_detected:
                confidence = detection_info['pose'].get('pose_confidence', 0.0)
                self.pose_status.setText(f"Status: Pose detected ({confidence:.2f})")
            else:
                self.pose_status.setText("Status: Active (no pose)")