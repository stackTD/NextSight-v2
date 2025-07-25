"""
Main application class for NextSight v2
Enhanced with zone management system for Phase 3
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

# Zone management imports
from nextsight.zones.zone_manager import ZoneManager
from nextsight.ui.context_menu import show_zone_context_menu, show_zone_properties_dialog

# Process management imports  
from nextsight.core.process_manager import ProcessManager


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
        self.zone_manager = None
        self.process_manager = None
        
        # Process zone creation tracking
        self.current_process_creation = None  # Track which process is being created
        self.current_process_zone_stage = None  # 'pick' or 'drop'
        self.current_process_id = None  # Explicit process ID tracking
        
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
            
            # Setup zone management system
            self.zone_manager = ZoneManager()
            
            # Setup process management system
            self.process_manager = ProcessManager()
            
            # Connect signals
            self.setup_connections()
            
            self.logger.info("Application components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to setup application: {e}")
            self.show_error_dialog("Application Setup Error", str(e))
            sys.exit(1)
    
    def setup_connections(self):
        """Setup signal connections between components"""
        if not self.main_window or not self.camera_thread or not self.zone_manager or not self.process_manager:
            return
        
        # Get references to UI components
        main_widget = self.main_window.get_main_widget()
        camera_widget = main_widget.get_camera_widget()
        status_bar = self.main_window.get_status_bar()
        control_panel = main_widget.get_control_panel()
        
        # Camera thread to UI connections
        self.camera_thread.frame_ready.connect(camera_widget.update_frame)
        self.camera_thread.frame_ready.connect(self.on_frame_ready)
        self.camera_thread.fps_update.connect(status_bar.update_fps)
        self.camera_thread.fps_update.connect(main_widget.update_fps_display)
        self.camera_thread.status_update.connect(status_bar.show_status_message)
        self.camera_thread.error_occurred.connect(status_bar.show_error_message)
        self.camera_thread.error_occurred.connect(self.on_camera_error)
        
        # Zone system connections
        self.camera_thread.zone_intersections_update.connect(camera_widget.update_zone_intersections)
        self.camera_thread.set_zone_manager(self.zone_manager)
        camera_widget.set_zone_manager(self.zone_manager)
        camera_widget.zone_context_menu_requested.connect(self.show_zone_context_menu)
        camera_widget.zone_modified.connect(self.on_zone_modified_by_editor)
        
        # Zone manager to status bar connections
        self.zone_manager.zone_status_changed.connect(status_bar.update_zone_status)
        self.zone_manager.pick_event_detected.connect(status_bar.on_pick_event)
        self.zone_manager.drop_event_detected.connect(status_bar.on_drop_event)
        
        # Process management connections
        self.zone_manager.process_pick_event.connect(self.process_manager.handle_pick_event)
        self.zone_manager.process_drop_event.connect(self.process_manager.handle_drop_event)
        self.process_manager.status_message.connect(status_bar.show_process_message)
        
        # Control panel process management connections
        control_panel.create_process_requested.connect(self.create_process)
        control_panel.delete_process_requested.connect(self.delete_process)
        control_panel.zone_creation_requested.connect(self.create_zone_for_process)
        
        # Zone creator status connections
        zone_creator = self.zone_manager.get_zone_creator()
        zone_creator.zone_creation_started.connect(lambda zone_type: status_bar.set_zone_creation_mode(zone_type))
        zone_creator.zone_creation_completed.connect(lambda zone: status_bar.set_zone_creation_mode(None))
        zone_creator.zone_creation_completed.connect(self.on_zone_created)
        zone_creator.zone_creation_cancelled.connect(lambda: status_bar.set_zone_creation_mode(None))
        
        # UI control connections (backward compatibility)
        main_widget.toggle_detection_requested.connect(self.toggle_hand_detection)
        main_widget.toggle_landmarks_requested.connect(self.toggle_landmarks)
        main_widget.toggle_connections_requested.connect(self.toggle_connections)
        main_widget.confidence_threshold_changed.connect(self.set_confidence_threshold)
        main_widget.camera_switch_requested.connect(self.switch_camera)
        
        # New Phase 2 control connections
        main_widget.toggle_hand_detection_requested.connect(self.toggle_hand_detection)
        main_widget.toggle_pose_detection_requested.connect(self.toggle_pose_detection)
        main_widget.toggle_pose_landmarks_requested.connect(self.toggle_pose_landmarks)
        main_widget.toggle_gesture_recognition_requested.connect(self.toggle_gesture_recognition)
        main_widget.reset_detection_settings_requested.connect(self.reset_detection_settings)
        
        # Keyboard control connections from main window
        self.main_window.toggle_hand_detection_requested.connect(self.toggle_hand_detection)
        self.main_window.toggle_pose_detection_requested.connect(self.toggle_pose_detection)
        self.main_window.toggle_pose_landmarks_requested.connect(self.toggle_pose_landmarks)
        self.main_window.toggle_gesture_recognition_requested.connect(self.toggle_gesture_recognition)
        self.main_window.reset_detection_settings_requested.connect(self.reset_detection_settings)
        self.main_window.toggle_landmarks_requested.connect(self.toggle_landmarks)
        self.main_window.toggle_connections_requested.connect(self.toggle_connections)
        self.main_window.exit_application_requested.connect(self.exit_application)
        
        # Zone keyboard control connections
        self.main_window.create_pick_zone_requested.connect(self.create_pick_zone)
        self.main_window.create_drop_zone_requested.connect(self.create_drop_zone)
        self.main_window.toggle_zones_requested.connect(self.toggle_zones)
        self.main_window.clear_zones_requested.connect(self.clear_zones)
        self.main_window.toggle_zone_editing_requested.connect(self.toggle_zone_editing)
        
        # Window close connection
        self.main_window.closeEvent = self.on_close_event
        
        self.logger.info("Signal connections established")
    
    def on_frame_ready(self, qt_image, detection_info):
        """Handle new frame from camera thread"""
        # Update status bar with detection info
        hands_count = 0
        pose_detected = False
        
        # Extract information from new detection format
        if 'hands' in detection_info:
            hands_count = detection_info['hands'].get('hands_detected', 0)
        if 'pose' in detection_info:
            pose_detected = detection_info['pose'].get('pose_detected', False)
        
        self.main_window.get_status_bar().update_hands_count(hands_count)
        if hasattr(self.main_window.get_status_bar(), 'update_pose_status'):
            self.main_window.get_status_bar().update_pose_status(pose_detected)
        
        # Update main widget with detection info
        self.main_window.get_main_widget().update_detection_info(detection_info)
    
    def on_camera_error(self, error_message):
        """Handle camera errors"""
        self.logger.error(f"Camera error: {error_message}")
        self.main_window.get_status_bar().set_camera_status(False)
    
    def toggle_hand_detection(self):
        """Toggle hand detection"""
        if self.camera_thread:
            enabled = self.camera_thread.toggle_hand_detection()
            self.main_window.get_status_bar().set_detection_status(enabled)
            self.logger.info(f"Hand detection {'enabled' if enabled else 'disabled'}")
    
    def toggle_pose_detection(self):
        """Toggle pose detection"""
        if self.camera_thread:
            enabled = self.camera_thread.toggle_pose_detection()
            # Update status bar if it supports pose status
            if hasattr(self.main_window.get_status_bar(), 'set_pose_status'):
                self.main_window.get_status_bar().set_pose_status(enabled)
            self.logger.info(f"Pose detection {'enabled' if enabled else 'disabled'}")
    
    def toggle_detection(self):
        """Toggle hand detection (for backward compatibility)"""
        self.toggle_hand_detection()
    
    def toggle_landmarks(self):
        """Toggle landmark visibility"""
        if self.camera_thread:
            enabled = self.camera_thread.toggle_landmarks()
            self.logger.info(f"Landmarks {'enabled' if enabled else 'disabled'}")
    
    def toggle_connections(self):
        """Toggle connection lines"""
        if self.camera_thread:
            enabled = self.camera_thread.toggle_connections()
            self.logger.info(f"Connections {'enabled' if enabled else 'disabled'}")
    
    def toggle_pose_landmarks(self):
        """Toggle pose landmark visibility"""
        if self.camera_thread:
            enabled = self.camera_thread.toggle_pose_landmarks()
            self.logger.info(f"Pose landmarks {'enabled' if enabled else 'disabled'}")
    
    def toggle_gesture_recognition(self):
        """Toggle gesture recognition"""
        if self.camera_thread:
            enabled = self.camera_thread.toggle_gesture_recognition()
            self.logger.info(f"Gesture recognition {'enabled' if enabled else 'disabled'}")
    
    def reset_detection_settings(self):
        """Reset all detection settings to defaults"""
        if self.camera_thread:
            self.camera_thread.reset_detection_settings()
            self.main_window.get_status_bar().set_detection_status(True)
            self.logger.info("Detection settings reset to defaults")
    
    def exit_application(self):
        """Exit the application gracefully"""
        self.logger.info("Exit application requested via keyboard")
        self.main_window.close()
    
    def set_confidence_threshold(self, threshold):
        """Set detection confidence threshold"""
        if self.camera_thread:
            self.camera_thread.set_confidence_threshold(threshold)
            self.logger.info(f"Confidence threshold set to {threshold:.2f}")
    
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
    
    def create_pick_zone(self):
        """Start creating a pick zone"""
        if self.zone_manager:
            success = self.zone_manager.start_zone_creation('pick')
            if success:
                self.main_window.get_status_bar().show_zone_message("Click and drag to create pick zone", 5000)
            self.logger.info("Pick zone creation started" if success else "Failed to start pick zone creation")
    
    def create_drop_zone(self):
        """Start creating a drop zone"""
        if self.zone_manager:
            success = self.zone_manager.start_zone_creation('drop')
            if success:
                self.main_window.get_status_bar().show_zone_message("Click and drag to create drop zone", 5000)
            self.logger.info("Drop zone creation started" if success else "Failed to start drop zone creation")
    
    def toggle_zones(self):
        """Toggle zone system on/off"""
        if self.zone_manager and self.camera_thread:
            current_state = self.zone_manager.is_enabled
            new_state = not current_state
            
            self.zone_manager.enable_detection(new_state)
            self.camera_thread.enable_zones(new_state)
            
            main_widget = self.main_window.get_main_widget()
            camera_widget = main_widget.get_camera_widget()
            camera_widget.enable_zones(new_state)
            
            # Update status bar with zone system state
            status_bar = self.main_window.get_status_bar()
            status_bar.set_zone_system_enabled(new_state)
            
            status = "enabled" if new_state else "disabled"
            self.logger.info(f"Zone system {status}")
    
    def toggle_zone_editing(self):
        """Toggle zone editing mode"""
        main_widget = self.main_window.get_main_widget()
        camera_widget = main_widget.get_camera_widget()
        
        # Toggle editing mode
        new_state = not camera_widget.zone_editing_enabled
        camera_widget.set_zone_editing_enabled(new_state)
        
        # Update status bar
        status_bar = self.main_window.get_status_bar()
        if new_state:
            status_bar.show_zone_message("Zone editing mode ENABLED - Click zones to edit", 3000)
        else:
            status_bar.show_zone_message("Zone editing mode DISABLED", 3000)
        
        status = "enabled" if new_state else "disabled"
        self.logger.info(f"Zone editing mode {status}")
    
    def on_zone_modified_by_editor(self, zone):
        """Handle zone modification from zone editor"""
        self.main_window.get_status_bar().show_zone_message(
            f"Zone '{zone.name}' modified", 2000
        )
        self.logger.info(f"Zone {zone.id} modified via editor")
    
    def clear_zones(self):
        """Clear all zones after confirmation"""
        if self.zone_manager:
            reply = QMessageBox.question(
                self.main_window,
                "Clear All Zones",
                "Are you sure you want to clear all zones?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.zone_manager.clear_all_zones()
                self.main_window.get_status_bar().show_zone_message("All zones cleared")
                self.logger.info("All zones cleared")
    
    def show_zone_context_menu(self, position, zone):
        """Show context menu for zone operations"""
        try:
            menu = show_zone_context_menu(position, zone, self.main_window)
            
            # Connect menu signals
            menu.create_pick_zone_requested.connect(self.create_pick_zone)
            menu.create_drop_zone_requested.connect(self.create_drop_zone)
            menu.clear_all_zones_requested.connect(self.clear_zones)
            menu.save_zones_requested.connect(self.save_zones)
            menu.load_zones_requested.connect(self.load_zones)
            
            if zone:
                menu.edit_zone_requested.connect(self.edit_zone)
                menu.delete_zone_requested.connect(self.delete_zone)
                menu.toggle_zone_active_requested.connect(self.toggle_zone_active)
            
        except Exception as e:
            self.logger.error(f"Error showing zone context menu: {e}")
    
    def edit_zone(self, zone_id: str):
        """Edit zone properties"""
        if self.zone_manager:
            zone = self.zone_manager.get_zone(zone_id)
            if zone:
                try:
                    properties = show_zone_properties_dialog(zone, self.main_window)
                    if properties:
                        # Update zone with new properties
                        for key, value in properties.items():
                            setattr(zone, key, value)
                        
                        self.zone_manager.update_zone(zone)
                        self.main_window.get_status_bar().show_zone_message(f"Zone {zone.name} updated")
                        self.logger.info(f"Zone {zone_id} updated")
                
                except Exception as e:
                    self.logger.error(f"Error editing zone {zone_id}: {e}")
    
    def delete_zone(self, zone_id: str):
        """Delete zone after confirmation"""
        if self.zone_manager:
            zone = self.zone_manager.get_zone(zone_id)
            if zone:
                reply = QMessageBox.question(
                    self.main_window,
                    "Delete Zone",
                    f"Delete zone '{zone.name}'?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    self.zone_manager.delete_zone(zone_id)
                    self.main_window.get_status_bar().show_zone_message(f"Zone {zone.name} deleted")
                    self.logger.info(f"Zone {zone_id} deleted")
    
    def toggle_zone_active(self, zone_id: str):
        """Toggle zone active state"""
        if self.zone_manager:
            zone = self.zone_manager.get_zone(zone_id)
            if zone:
                zone.active = not zone.active
                self.zone_manager.update_zone(zone)
                status = "activated" if zone.active else "deactivated"
                self.main_window.get_status_bar().show_zone_message(f"Zone {zone.name} {status}")
                self.logger.info(f"Zone {zone_id} {status}")
    
    def save_zones(self):
        """Save zone configuration"""
        if self.zone_manager:
            success = self.zone_manager.save_configuration()
            message = "Zones saved successfully" if success else "Failed to save zones"
            self.main_window.get_status_bar().show_zone_message(message)
            self.logger.info(message)
    
    def load_zones(self):
        """Load zone configuration"""
        if self.zone_manager:
            success = self.zone_manager.load_configuration()
            message = "Zones loaded successfully" if success else "Failed to load zones"
            self.main_window.get_status_bar().show_zone_message(message)
            self.logger.info(message)
    
    # Process Management Methods
    
    @pyqtSlot(str)
    def create_process(self, process_name: str):
        """Create a new process"""
        try:
            process = self.process_manager.create_process(process_name if process_name else None)
            
            # Add to control panel
            main_widget = self.main_window.get_main_widget()
            control_panel = main_widget.get_control_panel()
            control_panel.add_process_to_list(process)
            
            # Show instruction message and start pick zone creation
            self.show_info_dialog(
                "Create Process Zones",
                f"Now create zones for '{process.name}'.\n\n"
                "First, create the pick zone by clicking and dragging on the camera view."
            )
            
            # Extract process number from ID (e.g., "process_1" -> "1")
            process_number = process.id.split('_')[-1]
            
            # Start pick zone creation with explicit tracking
            self.current_process_id = process.id
            self.current_process_zone_stage = "pick"
            pick_zone_name = f"Pick Zone {process_number}"
            self.create_zone_for_process("PICK", pick_zone_name)
            
            self.logger.info(f"Created process: {process.name} ({process.id})")
            
        except Exception as e:
            self.logger.error(f"Failed to create process: {e}")
            self.show_error_dialog("Process Creation Error", str(e))
    
    @pyqtSlot(str)
    def delete_process(self, process_id: str):
        """Delete a process"""
        try:
            # Get associated zone IDs before deletion
            pick_zone_id, drop_zone_id = self.process_manager.get_process_zone_ids(process_id)
            
            # Delete the process
            success = self.process_manager.delete_process(process_id)
            
            if success:
                # Delete associated zones
                if pick_zone_id:
                    self.zone_manager.delete_zone(pick_zone_id)
                if drop_zone_id:
                    self.zone_manager.delete_zone(drop_zone_id)
                
                # Update control panel
                main_widget = self.main_window.get_main_widget()
                control_panel = main_widget.get_control_panel()
                control_panel.remove_process_from_list(process_id)
                
                self.logger.info(f"Deleted process: {process_id}")
            else:
                self.show_error_dialog("Process Deletion Error", "Failed to delete process")
                
        except Exception as e:
            self.logger.error(f"Failed to delete process: {e}")
            self.show_error_dialog("Process Deletion Error", str(e))
    
    @pyqtSlot(str, str)
    def create_zone_for_process(self, zone_type: str, zone_name: str):
        """Create a zone for a process"""
        try:
            # Start zone creation with custom name
            success = self.zone_manager.start_zone_creation(zone_type, zone_name)
            
            if success:
                status_bar = self.main_window.get_status_bar()
                status_bar.show_zone_message(f"Creating {zone_type} zone: {zone_name}")
                self.logger.info(f"Started creating {zone_type} zone: {zone_name}")
                
                # Track this as a process zone creation
                # The zone type in the name indicates which stage
                if "Pick Zone" in zone_name:
                    self.current_process_zone_stage = "pick"
                elif "Drop Zone" in zone_name:
                    self.current_process_zone_stage = "drop"
                
            else:
                self.show_error_dialog("Zone Creation Error", f"Failed to start {zone_type} zone creation")
                
        except Exception as e:
            self.logger.error(f"Failed to create zone for process: {e}")
            self.show_error_dialog("Zone Creation Error", str(e))
    
    @pyqtSlot(object)
    def on_zone_created(self, zone):
        """Handle zone creation completion"""
        try:
            # Check if this is a process zone using explicit tracking
            if self.current_process_zone_stage and self.current_process_id:
                # Get the process using tracked ID
                process = self.process_manager.get_process(self.current_process_id)
                if process:
                    if self.current_process_zone_stage == "pick":
                        # Associate pick zone and start drop zone creation
                        self.process_manager.associate_zones(self.current_process_id, zone.id, process.drop_zone_id)
                        
                        # Automatically start drop zone creation immediately
                        process_number = self.current_process_id.split('_')[-1]
                        drop_zone_name = f"Drop Zone {process_number}"
                        self.current_process_zone_stage = "drop"  # Update stage
                        self.create_zone_for_process("DROP", drop_zone_name)
                        
                        # Show non-blocking status message
                        self.main_window.get_status_bar().show_process_message(
                            f"Pick zone created! Now creating drop zone for {process.name}...", "green"
                        )
                        
                    elif self.current_process_zone_stage == "drop":
                        # Associate drop zone and complete process creation
                        pick_zone_id, _ = self.process_manager.get_process_zone_ids(self.current_process_id)
                        self.process_manager.associate_zones(self.current_process_id, pick_zone_id, zone.id)
                        
                        # Update control panel
                        main_widget = self.main_window.get_main_widget()
                        control_panel = main_widget.get_control_panel()
                        control_panel.update_process_in_list(process)
                        
                        # Show completion message
                        self.show_info_dialog(
                            "Process Created Successfully",
                            f"Process '{process.name}' has been created with pick and drop zones!\n\n"
                            "You can now use the pick and drop zones for workflow operations."
                        )
                        
                        # Clear process creation tracking
                        self.current_process_zone_stage = None
                        self.current_process_id = None
                else:
                    self.logger.warning(f"Process {self.current_process_id} not found for zone association")
                    # Clear tracking on error
                    self.current_process_zone_stage = None
                    self.current_process_id = None
                    
        except Exception as e:
            self.logger.error(f"Error handling zone creation: {e}")
            # Clear tracking on error
            self.current_process_zone_stage = None
            self.current_process_id = None
            self.show_error_dialog("Zone Creation Error", str(e))
    
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