"""
Main application class for NextSight v2
"""

import sys
import logging
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer, pyqtSlot
from PyQt6.QtGui import QIcon
from nextsight.core.window import MainWindow
from nextsight.core.camera_thread import CameraThread
from nextsight.ui.styles import apply_dark_theme
from nextsight.utils.config import config


class NextSightApplication:
    """Main NextSight v2 application"""
    
    def __init__(self):
        # Setup logging
        self.setup_logging()
        
        # Initialize Qt application
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("NextSight v2")
        self.app.setApplicationVersion("2.0.0")
        self.app.setOrganizationName("NextSight Team")
        
        # Apply dark theme
        apply_dark_theme(self.app)
        
        # Initialize components
        self.main_window = None
        self.camera_thread = None
        
        # Setup application
        self.setup_application()
    
    def setup_logging(self):
        """Setup application logging"""
        logging.basicConfig(
            level=getattr(logging, config.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("NextSight v2 starting up...")
    
    def setup_application(self):
        """Setup the main application components"""
        try:
            # Create main window
            self.main_window = MainWindow()
            
            # Setup camera thread
            self.camera_thread = CameraThread()
            
            # Connect signals
            self.setup_connections()
            
            self.logger.info("Application components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to setup application: {e}")
            self.show_error_dialog("Application Setup Error", str(e))
            sys.exit(1)
    
    def setup_connections(self):
        """Setup signal connections between components"""
        if not self.main_window or not self.camera_thread:
            return
        
        # Get references to UI components
        main_widget = self.main_window.get_main_widget()
        camera_widget = main_widget.get_camera_widget()
        status_bar = self.main_window.get_status_bar()
        
        # Camera thread to UI connections
        self.camera_thread.frame_ready.connect(camera_widget.update_frame)
        self.camera_thread.frame_ready.connect(self.on_frame_ready)
        self.camera_thread.fps_update.connect(status_bar.update_fps)
        self.camera_thread.fps_update.connect(main_widget.update_fps_display)
        self.camera_thread.status_update.connect(status_bar.show_status_message)
        self.camera_thread.error_occurred.connect(status_bar.show_error_message)
        self.camera_thread.error_occurred.connect(self.on_camera_error)
        
        # UI control connections
        main_widget.toggle_detection_requested.connect(self.toggle_detection)
        main_widget.toggle_landmarks_requested.connect(self.toggle_landmarks)
        main_widget.toggle_connections_requested.connect(self.toggle_connections)
        main_widget.confidence_threshold_changed.connect(self.set_confidence_threshold)
        main_widget.camera_switch_requested.connect(self.switch_camera)
        
        # Window close connection
        self.main_window.closeEvent = self.on_close_event
        
        self.logger.info("Signal connections established")
    
    @pyqtSlot(object, dict)
    def on_frame_ready(self, qt_image, detection_info):
        """Handle new frame from camera thread"""
        # Update status bar with detection info
        hands_count = detection_info.get('hands_detected', 0)
        self.main_window.get_status_bar().update_hands_count(hands_count)
        
        # Update main widget with detection info
        self.main_window.get_main_widget().update_detection_info(detection_info)
    
    @pyqtSlot(str)
    def on_camera_error(self, error_message):
        """Handle camera errors"""
        self.logger.error(f"Camera error: {error_message}")
        self.main_window.get_status_bar().set_camera_status(False)
    
    @pyqtSlot()
    def toggle_detection(self):
        """Toggle hand detection"""
        if self.camera_thread:
            enabled = self.camera_thread.toggle_hand_detection()
            self.main_window.get_status_bar().set_detection_status(enabled)
            self.logger.info(f"Hand detection {'enabled' if enabled else 'disabled'}")
    
    @pyqtSlot()
    def toggle_landmarks(self):
        """Toggle landmark visibility"""
        if self.camera_thread:
            enabled = self.camera_thread.toggle_landmarks()
            self.logger.info(f"Landmarks {'enabled' if enabled else 'disabled'}")
    
    @pyqtSlot()
    def toggle_connections(self):
        """Toggle connection lines"""
        if self.camera_thread:
            enabled = self.camera_thread.toggle_connections()
            self.logger.info(f"Connections {'enabled' if enabled else 'disabled'}")
    
    @pyqtSlot(float)
    def set_confidence_threshold(self, threshold):
        """Set detection confidence threshold"""
        if self.camera_thread:
            self.camera_thread.set_confidence_threshold(threshold)
            self.logger.info(f"Confidence threshold set to {threshold:.2f}")
    
    @pyqtSlot(int)
    def switch_camera(self, camera_index):
        """Switch to different camera"""
        if self.camera_thread:
            self.camera_thread.switch_camera(camera_index)
            self.logger.info(f"Switched to camera {camera_index}")
    
    def start_camera(self):
        """Start the camera thread"""
        if self.camera_thread and not self.camera_thread.isRunning():
            self.camera_thread.start()
            
            # Update status after a brief delay to allow initialization
            QTimer.singleShot(1000, lambda: self.main_window.get_status_bar().set_camera_status(True))
            
            self.logger.info("Camera thread started")
    
    def stop_camera(self):
        """Stop the camera thread"""
        if self.camera_thread and self.camera_thread.isRunning():
            self.camera_thread.stop()
            self.main_window.get_status_bar().set_camera_status(False)
            self.logger.info("Camera thread stopped")
    
    def run(self):
        """Run the application"""
        try:
            # Show main window
            self.main_window.show()
            
            # Start camera after window is shown
            QTimer.singleShot(500, self.start_camera)
            
            self.logger.info("NextSight v2 application started successfully")
            
            # Run application event loop
            return self.app.exec()
            
        except Exception as e:
            self.logger.error(f"Application runtime error: {e}")
            self.show_error_dialog("Runtime Error", str(e))
            return 1
    
    def on_close_event(self, event):
        """Handle application close event"""
        self.logger.info("Application closing...")
        
        # Stop camera thread
        self.stop_camera()
        
        # Cleanup
        self.cleanup()
        
        event.accept()
    
    def cleanup(self):
        """Cleanup application resources"""
        try:
            if self.camera_thread:
                self.camera_thread.cleanup()
            
            self.logger.info("Application cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")
    
    def show_error_dialog(self, title: str, message: str):
        """Show error dialog to user"""
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()
    
    def show_info_dialog(self, title: str, message: str):
        """Show information dialog to user"""
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()


def create_application() -> NextSightApplication:
    """Factory function to create the application"""
    return NextSightApplication()