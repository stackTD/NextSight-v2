"""
Main window with custom title bar for NextSight v2
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QFrame, QApplication, QMessageBox)
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QPixmap, QPainter, QColor, QKeyEvent
from nextsight.ui.main_widget import MainWidget
from nextsight.ui.status_bar import StatusBar
from nextsight.utils.config import config
from nextsight.utils.detection_config import detection_config, get_keyboard_help
import logging


class CustomTitleBar(QWidget):
    """Custom title bar with NextSight branding"""
    
    # Signals
    minimize_clicked = pyqtSignal()
    maximize_clicked = pyqtSignal()
    close_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("titleBar")
        self.setFixedHeight(40)
        
        # For window dragging
        self.dragging = False
        self.drag_position = QPoint()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup custom title bar UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Logo/Icon (placeholder - you can add actual logo later)
        self.logo_label = QLabel()
        self.logo_label.setFixedSize(32, 32)
        self.logo_label.setStyleSheet("margin: 4px;")
        
        # Create a simple logo placeholder
        logo_pixmap = self.create_logo_pixmap()
        self.logo_label.setPixmap(logo_pixmap)
        layout.addWidget(self.logo_label)
        
        # Title
        self.title_label = QLabel("NextSight")
        self.title_label.setObjectName("titleLabel")
        self.title_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)
        
        # Stretch to push buttons to right
        layout.addStretch()
        
        # Window control buttons
        self.minimize_btn = QPushButton("−")
        self.minimize_btn.setObjectName("titleButton")
        self.minimize_btn.setFixedSize(40, 40)
        self.minimize_btn.setFont(QFont("Arial", 16))
        self.minimize_btn.clicked.connect(self.minimize_clicked.emit)
        layout.addWidget(self.minimize_btn)
        
        self.maximize_btn = QPushButton("□")
        self.maximize_btn.setObjectName("titleButton")
        self.maximize_btn.setFixedSize(40, 40)
        self.maximize_btn.setFont(QFont("Arial", 12))
        self.maximize_btn.clicked.connect(self.maximize_clicked.emit)
        layout.addWidget(self.maximize_btn)
        
        self.close_btn = QPushButton("×")
        self.close_btn.setObjectName("closeButton")
        self.close_btn.setFixedSize(40, 40)
        self.close_btn.setFont(QFont("Arial", 16))
        self.close_btn.clicked.connect(self.close_clicked.emit)
        layout.addWidget(self.close_btn)
    
    def create_logo_pixmap(self) -> QPixmap:
        """Create a simple logo placeholder"""
        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw a simple eye-like logo
        painter.setBrush(QColor("#007ACC"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(2, 6, 20, 12)
        
        painter.setBrush(QColor("#ffffff"))
        painter.drawEllipse(8, 9, 8, 6)
        
        painter.setBrush(QColor("#007ACC"))
        painter.drawEllipse(10, 10, 4, 4)
        
        painter.end()
        return pixmap
    
    def mousePressEvent(self, event):
        """Handle mouse press for window dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.window().frameGeometry().topLeft()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for window dragging"""
        if event.buttons() == Qt.MouseButton.LeftButton and self.dragging:
            self.window().move(event.globalPosition().toPoint() - self.drag_position)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        self.dragging = False
    
    def mouseDoubleClickEvent(self, event):
        """Handle double click to maximize/restore"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.maximize_clicked.emit()


class MainWindow(QMainWindow):
    """Main application window with custom title bar and keyboard controls"""
    
    # Signals for keyboard actions
    toggle_hand_detection_requested = pyqtSignal()
    toggle_pose_detection_requested = pyqtSignal()
    toggle_pose_landmarks_requested = pyqtSignal()
    toggle_gesture_recognition_requested = pyqtSignal()
    reset_detection_settings_requested = pyqtSignal()
    toggle_landmarks_requested = pyqtSignal()
    toggle_connections_requested = pyqtSignal()
    exit_application_requested = pyqtSignal()
    
    # Zone management signals
    create_pick_zone_requested = pyqtSignal()
    create_drop_zone_requested = pyqtSignal()
    toggle_zones_requested = pyqtSignal()
    clear_zones_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        # Window state
        self.is_maximized = False
        self.normal_geometry = None
        
        # Keyboard controls
        self.keyboard_enabled = True
        self.logger = logging.getLogger(__name__)
        
        self.setup_window()
        self.setup_ui()
        self.setup_connections()
    
    def setup_window(self):
        """Setup window properties"""
        # Remove default title bar
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        # Set window properties
        self.setWindowTitle(config.ui.window_title)
        self.setMinimumSize(config.ui.min_width, config.ui.min_height)
        self.resize(config.ui.window_width, config.ui.window_height)
        
        # Enable focus for keyboard events
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Center window on screen
        self.center_on_screen()
    
    def keyPressEvent(self, event: QKeyEvent):
        """Handle keyboard shortcuts for detection controls"""
        if not self.keyboard_enabled:
            super().keyPressEvent(event)
            return
        
        key = event.key()
        key_text = event.text().lower()
        
        # Map keyboard shortcuts to actions
        try:
            if key_text == 'h':
                self.toggle_hand_detection_requested.emit()
                self.logger.info("Keyboard: Hand detection toggle requested")
                
            elif key_text == 'b':
                self.toggle_pose_detection_requested.emit()
                self.logger.info("Keyboard: Pose detection toggle requested")
                
            elif key_text == 'p':
                self.toggle_pose_landmarks_requested.emit()
                self.logger.info("Keyboard: Pose landmarks toggle requested")
                
            elif key_text == 'g':
                self.logger.info("Keyboard: Gesture recognition toggle requested")
                
            elif key_text == 'l':
                self.toggle_landmarks_requested.emit()
                self.logger.info("Keyboard: Landmarks toggle requested")
                
            elif key_text == 'c':
                self.toggle_connections_requested.emit()
                self.logger.info("Keyboard: Connections toggle requested")
                
            elif key_text == 'r':
                self.reset_detection_settings_requested.emit()
                self.logger.info("Keyboard: Reset detection settings requested")
                
            elif key_text == 'z':
                self.toggle_zones_requested.emit()
                self.logger.info("Keyboard: Toggle zones requested")
                
            elif key_text == '1':
                self.create_pick_zone_requested.emit()
                self.logger.info("Keyboard: Create pick zone requested")
                
            elif key_text == '2':
                self.create_drop_zone_requested.emit()
                self.logger.info("Keyboard: Create drop zone requested")
                
            elif key == Qt.Key.Key_Delete:
                self.clear_zones_requested.emit()
                self.logger.info("Keyboard: Clear zones requested")
                
            elif key == Qt.Key.Key_Escape:
                self.exit_application_requested.emit()
                self.logger.info("Keyboard: Exit application requested")
                
            elif key == Qt.Key.Key_F1:
                self.show_keyboard_help()
                
            else:
                # Pass unhandled keys to parent
                super().keyPressEvent(event)
                
        except Exception as e:
            self.logger.error(f"Error handling keyboard event: {e}")
            super().keyPressEvent(event)
    
    def show_keyboard_help(self):
        """Show keyboard shortcuts help dialog"""
        help_text = """KEYBOARD CONTROLS:

DETECTION CONTROLS:
H - Toggle hand detection
B - Toggle pose detection  
P - Toggle pose landmarks
G - Toggle gesture recognition
L - Toggle landmarks display
C - Toggle connections display
R - Reset all detection settings

ZONE CONTROLS:
Z - Toggle zone system
1 - Create pick zone (click & drag)
2 - Create drop zone (click & drag)
Delete - Clear all zones
Right-click - Zone context menu

SYSTEM:
F1 - Show this help dialog
ESC - Exit application"""
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("NextSight - Keyboard Controls")
        msg_box.setText(help_text)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()
    
    def set_keyboard_controls_enabled(self, enabled: bool):
        """Enable or disable keyboard controls"""
        self.keyboard_enabled = enabled
        self.logger.info(f"Keyboard controls {'enabled' if enabled else 'disabled'}")
    
    def center_on_screen(self):
        """Center the window on screen"""
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move(
            int((screen.width() - size.width()) / 2),
            int((screen.height() - size.height()) / 2)
        )
    
    def setup_ui(self):
        """Setup the user interface"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Custom title bar
        self.title_bar = CustomTitleBar()
        main_layout.addWidget(self.title_bar)
        
        # Content area
        content_frame = QFrame()
        content_frame.setFrameStyle(QFrame.Shape.Box)
        content_frame.setStyleSheet("border: 1px solid #3e3e42;")
        main_layout.addWidget(content_frame)
        
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Main widget
        self.main_widget = MainWidget()
        content_layout.addWidget(self.main_widget)
        
        # Status bar
        self.status_bar = StatusBar()
        self.setStatusBar(self.status_bar)
    
    def setup_connections(self):
        """Setup signal connections"""
        # Title bar signals
        self.title_bar.minimize_clicked.connect(self.showMinimized)
        self.title_bar.maximize_clicked.connect(self.toggle_maximize)
        self.title_bar.close_clicked.connect(self.close)
    
    def toggle_maximize(self):
        """Toggle between maximized and normal window state"""
        if self.is_maximized:
            self.restore_window()
        else:
            self.maximize_window()
    
    def maximize_window(self):
        """Maximize the window"""
        if not self.is_maximized:
            self.normal_geometry = self.geometry()
            screen = QApplication.primaryScreen().availableGeometry()
            self.setGeometry(screen)
            self.is_maximized = True
            self.title_bar.maximize_btn.setText("❐")
    
    def restore_window(self):
        """Restore window to normal size"""
        if self.is_maximized and self.normal_geometry:
            self.setGeometry(self.normal_geometry)
            self.is_maximized = False
            self.title_bar.maximize_btn.setText("□")
    
    def get_main_widget(self) -> MainWidget:
        """Get reference to main widget"""
        return self.main_widget
    
    def get_status_bar(self) -> StatusBar:
        """Get reference to status bar"""
        return self.status_bar
    
    def closeEvent(self, event):
        """Handle window close event"""
        # This will be handled by the application to properly clean up
        event.accept()
    
    def resizeEvent(self, event):
        """Handle window resize"""
        super().resizeEvent(event)
        # Update maximized state if needed
        if self.is_maximized:
            screen = QApplication.primaryScreen().availableGeometry()
            if self.geometry() != screen:
                self.is_maximized = False
                self.title_bar.maximize_btn.setText("□")
    
    def showEvent(self, event):
        """Handle window show event"""
        super().showEvent(event)
        # Set ready state after window is shown
        if hasattr(self, 'status_bar'):
            self.status_bar.set_ready_state()