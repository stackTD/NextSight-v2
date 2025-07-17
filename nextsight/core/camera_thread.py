"""
Camera thread implementation for smooth video capture and processing
"""

import cv2
import time
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal, QMutex, QWaitCondition
from PyQt6.QtGui import QImage
from typing import Optional
from nextsight.utils.config import config
from nextsight.vision.detector import MultiModalDetector


class CameraThread(QThread):
    """Thread for camera capture and processing"""
    
    # Signals
    frame_ready = pyqtSignal(object, dict)  # Processed frame and detection info
    status_update = pyqtSignal(str)  # Status messages
    error_occurred = pyqtSignal(str)  # Error messages
    fps_update = pyqtSignal(float)  # FPS updates
    zone_intersections_update = pyqtSignal(dict)  # Zone intersection data
    
    def __init__(self, camera_index: int = None):
        super().__init__()
        
        # Camera settings
        self.camera_index = camera_index or config.camera.default_index
        self.camera = None
        self.is_running = False
        self.is_paused = False
        
        # Thread synchronization
        self.mutex = QMutex()
        self.pause_condition = QWaitCondition()
        
        # Multi-modal detection (hands + pose)
        self.detector = MultiModalDetector()
        
        # Performance tracking
        self.fps_counter = 0
        self.fps_timer = time.time()
        self.frame_times = []
        
        # Frame processing
        self.frame_skip = 0  # Skip frames if processing is slow
        self.max_frame_skip = 3
        
        # Zone management integration
        self.zone_manager = None
        self.zones_enabled = False
        
    def initialize_camera(self) -> bool:
        """Initialize the camera with optimal settings"""
        try:
            self.camera = cv2.VideoCapture(self.camera_index)
            
            if not self.camera.isOpened():
                self.error_occurred.emit(f"Failed to open camera {self.camera_index}")
                return False
            
            # Set camera properties for optimal performance
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, config.camera.width)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, config.camera.height)
            self.camera.set(cv2.CAP_PROP_FPS, config.camera.fps)
            
            # Enable auto-exposure and auto-focus for better image quality
            self.camera.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.75)
            
            # Verify settings
            actual_width = int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
            actual_fps = self.camera.get(cv2.CAP_PROP_FPS)
            
            self.status_update.emit(
                f"Camera initialized: {actual_width}x{actual_height} @ {actual_fps:.1f}fps"
            )
            
            return True
            
        except Exception as e:
            self.error_occurred.emit(f"Camera initialization error: {str(e)}")
            return False
    
    def run(self):
        """Main thread execution"""
        if not self.initialize_camera():
            return
        
        self.is_running = True
        self.status_update.emit("Camera thread started")
        
        try:
            while self.is_running:
                # Handle pause state
                self.mutex.lock()
                if self.is_paused:
                    self.pause_condition.wait(self.mutex)
                self.mutex.unlock()
                
                if not self.is_running:
                    break
                
                # Capture frame
                ret, frame = self.camera.read()
                if not ret:
                    self.error_occurred.emit("Failed to capture frame")
                    continue
                
                # Skip frames if processing is behind
                if self.frame_skip > 0:
                    self.frame_skip -= 1
                    continue
                
                # Process frame timing
                frame_start = time.time()
                
                # Flip frame horizontally for mirror effect
                frame = cv2.flip(frame, 1)
                
                # Process with multi-modal detection
                processed_frame, detection_info = self.detector.process_frame(frame)
                
                # Process zone intersections if enabled
                zone_intersections = {}
                if self.zone_manager and self.zones_enabled:
                    try:
                        zone_results = self.zone_manager.process_frame_detections(detection_info)
                        zone_intersections = zone_results.get('intersections', {})
                        self.zone_intersections_update.emit(zone_intersections)
                    except Exception as e:
                        self.error_occurred.emit(f"Zone processing error: {str(e)}")
                
                # Convert to QImage for display
                qt_image = self.cv_to_qt_image(processed_frame)
                
                # Emit processed frame
                self.frame_ready.emit(qt_image, detection_info)
                
                # Update performance metrics
                self.update_performance_metrics(frame_start)
                
                # Yield to other threads
                self.msleep(1)
                
        except Exception as e:
            self.error_occurred.emit(f"Camera thread error: {str(e)}")
        finally:
            self.cleanup()
    
    def cv_to_qt_image(self, cv_img: np.ndarray) -> QImage:
        """Convert OpenCV image to QImage"""
        try:
            height, width, channel = cv_img.shape
            bytes_per_line = 3 * width
            
            # Convert BGR to RGB
            rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
            
            # Create QImage
            qt_image = QImage(
                rgb_image.data,
                width,
                height,
                bytes_per_line,
                QImage.Format.Format_RGB888
            )
            
            return qt_image
            
        except Exception as e:
            self.error_occurred.emit(f"Image conversion error: {str(e)}")
            # Return empty image on error
            return QImage()
    
    def update_performance_metrics(self, frame_start: float):
        """Update FPS and performance metrics"""
        frame_time = time.time() - frame_start
        self.frame_times.append(frame_time)
        
        # Keep only recent frame times
        if len(self.frame_times) > 30:
            self.frame_times.pop(0)
        
        # Update FPS counter
        self.fps_counter += 1
        current_time = time.time()
        
        if current_time - self.fps_timer >= 1.0:  # Update every second
            fps = self.fps_counter / (current_time - self.fps_timer)
            self.fps_update.emit(fps)
            
            # Check if we need to skip frames
            avg_frame_time = sum(self.frame_times) / len(self.frame_times)
            target_frame_time = 1.0 / config.target_fps
            
            if avg_frame_time > target_frame_time * 1.5:
                self.frame_skip = min(self.max_frame_skip, int(avg_frame_time / target_frame_time))
            
            # Reset counters
            self.fps_counter = 0
            self.fps_timer = current_time
    
    def pause(self):
        """Pause the camera thread"""
        self.mutex.lock()
        self.is_paused = True
        self.mutex.unlock()
        self.status_update.emit("Camera paused")
    
    def resume(self):
        """Resume the camera thread"""
        self.mutex.lock()
        self.is_paused = False
        self.pause_condition.wakeAll()
        self.mutex.unlock()
        self.status_update.emit("Camera resumed")
    
    def stop(self):
        """Stop the camera thread"""
        self.is_running = False
        
        # Wake up if paused
        self.mutex.lock()
        self.is_paused = False
        self.pause_condition.wakeAll()
        self.mutex.unlock()
        
        # Wait for thread to finish
        self.wait(3000)  # 3 second timeout
        self.status_update.emit("Camera stopped")
    
    def switch_camera(self, camera_index: int):
        """Switch to a different camera"""
        was_running = self.is_running
        
        if was_running:
            self.stop()
        
        self.camera_index = camera_index
        
        if was_running:
            self.start()
    
    def get_detection_stats(self) -> dict:
        """Get multi-modal detection statistics"""
        return self.detector.get_detection_stats()
    
    def toggle_hand_detection(self) -> bool:
        """Toggle hand detection"""
        return self.detector.toggle_hand_detection()
    
    def toggle_pose_detection(self) -> bool:
        """Toggle pose detection"""
        return self.detector.toggle_pose_detection()
    
    def toggle_landmarks(self) -> bool:
        """Toggle landmark visibility (hands)"""
        return self.detector.toggle_hand_landmarks()
    
    def toggle_connections(self) -> bool:
        """Toggle connection lines (hands)"""
        return self.detector.toggle_hand_connections()
    
    def toggle_pose_landmarks(self) -> bool:
        """Toggle pose landmark visibility"""
        return self.detector.toggle_pose_landmarks()
    
    def toggle_gesture_recognition(self) -> bool:
        """Toggle gesture recognition"""
        return self.detector.toggle_gesture_recognition()
    
    def reset_detection_settings(self):
        """Reset all detection settings"""
        self.detector.reset_detection_settings()
    
    def set_confidence_threshold(self, threshold: float):
        """Set detection confidence threshold"""
        self.detector.set_confidence_threshold(threshold)
    
    def cleanup(self):
        """Clean up resources"""
        if self.camera:
            self.camera.release()
            self.camera = None
        
        self.detector.cleanup()
        self.status_update.emit("Camera resources cleaned up")
    
    def set_zone_manager(self, zone_manager):
        """Set zone manager for zone detection"""
        self.zone_manager = zone_manager
        if zone_manager:
            self.zones_enabled = True
            self.status_update.emit("Zone detection enabled")
    
    def enable_zones(self, enabled: bool = True):
        """Enable or disable zone detection"""
        self.zones_enabled = enabled and self.zone_manager is not None
        status = "enabled" if self.zones_enabled else "disabled"
        self.status_update.emit(f"Zone detection {status}")