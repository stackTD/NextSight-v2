"""
Process management widget for NextSight v2
UI components for creating and managing processes
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QListWidget, QListWidgetItem, QMessageBox,
                             QInputDialog, QGroupBox, QScrollArea)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
import logging

from nextsight.core.process_manager import Process


class ProcessListWidget(QWidget):
    """Widget for displaying and managing the list of processes"""
    
    # Signals
    create_process_requested = pyqtSignal()
    delete_process_requested = pyqtSignal(str)  # process_id
    process_selected = pyqtSignal(str)  # process_id
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.processes = {}
        self.logger = logging.getLogger(__name__)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the process list UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Create Process button
        self.create_btn = QPushButton("Create Process +")
        self.create_btn.setObjectName("createProcessButton")
        self.create_btn.setStyleSheet("""
            QPushButton#createProcessButton {
                background-color: #007ACC;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12pt;
            }
            QPushButton#createProcessButton:hover {
                background-color: #005a9e;
            }
            QPushButton#createProcessButton:pressed {
                background-color: #004785;
            }
        """)
        self.create_btn.clicked.connect(self.on_create_process)
        layout.addWidget(self.create_btn)
        
        # Process list
        self.process_list = QListWidget()
        self.process_list.setStyleSheet("""
            QListWidget {
                background-color: #2b2b2b;
                border: 1px solid #3e3e42;
                selection-background-color: #007ACC;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #3e3e42;
            }
            QListWidget::item:hover {
                background-color: #3e3e42;
            }
        """)
        layout.addWidget(self.process_list)
        
        # Status label
        self.status_label = QLabel("No processes created")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #888888; font-style: italic;")
        layout.addWidget(self.status_label)
    
    def add_process(self, process: Process):
        """Add a process to the list"""
        self.processes[process.id] = process
        self.refresh_list()
    
    def remove_process(self, process_id: str):
        """Remove a process from the list"""
        if process_id in self.processes:
            del self.processes[process_id]
            self.refresh_list()
    
    def update_process(self, process: Process):
        """Update a process in the list"""
        self.processes[process.id] = process
        self.refresh_list()
    
    def refresh_list(self):
        """Refresh the process list display"""
        self.process_list.clear()
        
        if not self.processes:
            self.status_label.setText("No processes created")
            self.status_label.show()
            return
        
        self.status_label.hide()
        
        for process in self.processes.values():
            item_widget = ProcessItemWidget(process)
            item_widget.delete_requested.connect(self.on_delete_process)
            
            list_item = QListWidgetItem()
            list_item.setSizeHint(item_widget.sizeHint())
            
            self.process_list.addItem(list_item)
            self.process_list.setItemWidget(list_item, item_widget)
    
    def on_create_process(self):
        """Handle create process button click"""
        self.create_process_requested.emit()
    
    def on_delete_process(self, process_id: str):
        """Handle delete process request"""
        if process_id in self.processes:
            process = self.processes[process_id]
            reply = QMessageBox.question(
                self, 
                "Delete Process", 
                f"Are you sure you want to delete '{process.name}'?\nThis will also delete its associated zones.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.delete_process_requested.emit(process_id)


class ProcessItemWidget(QWidget):
    """Widget for displaying a single process item"""
    
    delete_requested = pyqtSignal(str)  # process_id
    
    def __init__(self, process: Process, parent=None):
        super().__init__(parent)
        self.process = process
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the process item UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Process info
        info_layout = QVBoxLayout()
        
        # Process name
        name_label = QLabel(self.process.name)
        name_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        name_label.setStyleSheet("color: #ffffff;")
        info_layout.addWidget(name_label)
        
        # Process status
        status_parts = []
        
        if self.process.pick_zone_id and self.process.drop_zone_id:
            status_parts.append("✓ Zones configured")
        else:
            missing = []
            if not self.process.pick_zone_id:
                missing.append("pick zone")
            if not self.process.drop_zone_id:
                missing.append("drop zone")
            status_parts.append(f"⚠ Missing: {', '.join(missing)}")
        
        if self.process.completed_count > 0:
            status_parts.append(f"Completed: {self.process.completed_count}")
        
        if self.process.error_count > 0:
            status_parts.append(f"Errors: {self.process.error_count}")
        
        status_text = " | ".join(status_parts)
        status_label = QLabel(status_text)
        status_label.setStyleSheet("color: #bbbbbb; font-size: 9pt;")
        info_layout.addWidget(status_label)
        
        layout.addLayout(info_layout)
        
        # Spacer
        layout.addStretch()
        
        # Delete button
        delete_btn = QPushButton("Delete")
        delete_btn.setObjectName("deleteButton")
        delete_btn.setStyleSheet("""
            QPushButton#deleteButton {
                background-color: #ff6b6b;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
                font-size: 9pt;
            }
            QPushButton#deleteButton:hover {
                background-color: #ff5252;
            }
            QPushButton#deleteButton:pressed {
                background-color: #d32f2f;
            }
        """)
        delete_btn.clicked.connect(lambda: self.delete_requested.emit(self.process.id))
        layout.addWidget(delete_btn)


class ProcessManagementWidget(QWidget):
    """Main widget for process management interface"""
    
    # Signals
    zone_creation_requested = pyqtSignal(str, str)  # zone_type, zone_name
    process_created = pyqtSignal(object)  # Process
    process_deleted = pyqtSignal(str)  # process_id
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_process_creation = None  # Track ongoing process creation
        self.logger = logging.getLogger(__name__)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the process management UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title_label = QLabel("Process Management")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #007ACC; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Process list
        self.process_list = ProcessListWidget()
        self.process_list.create_process_requested.connect(self.on_create_process_requested)
        self.process_list.delete_process_requested.connect(self.on_delete_process_requested)
        layout.addWidget(self.process_list)
        
        # Instructions
        instructions = QLabel(
            "Create processes to define pick-and-drop workflows.\n"
            "Each process requires a pick zone and a drop zone."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #888888; font-size: 9pt; font-style: italic;")
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(instructions)
    
    def add_process(self, process):
        """Add a process to the list"""
        self.process_list.add_process(process)
    
    def remove_process(self, process_id: str):
        """Remove a process from the list"""
        self.process_list.remove_process(process_id)
    
    def update_process(self, process):
        """Update a process in the list"""
        self.process_list.update_process(process)
    
    def on_create_process_requested(self):
        """Handle request to create a new process"""
        self.logger.info("Process creation requested")
        
        # Get process name from user
        name, ok = QInputDialog.getText(
            self, 
            "Create Process", 
            "Enter process name (or leave empty for default):",
            text=""
        )
        
        if ok:
            # Signal to create the process
            from nextsight.core.process_manager import ProcessManager
            # This will be handled by the main application
            self.process_created.emit(name if name.strip() else None)
    
    def on_delete_process_requested(self, process_id: str):
        """Handle request to delete a process"""
        self.logger.info(f"Process deletion requested: {process_id}")
        self.process_deleted.emit(process_id)
    
    def start_zone_creation_flow(self, process_id: str, process_name: str):
        """Start the zone creation flow for a process"""
        self.current_process_creation = process_id
        
        # Show message about creating pick zone
        QMessageBox.information(
            self,
            "Create Process Zones",
            f"Now create the pick zone for '{process_name}'.\n\n"
            "Click OK and then use the zone creation tools to create the pick zone."
        )
        
        # Request pick zone creation
        pick_zone_name = f"Pick Zone {process_name.split()[-1]}"  # Extract number from "Process N"
        self.zone_creation_requested.emit("PICK", pick_zone_name)
    
    def on_pick_zone_created(self, zone_id: str, process_id: str, process_name: str):
        """Handle pick zone creation completion"""
        # Show message about creating drop zone
        QMessageBox.information(
            self,
            "Create Drop Zone",
            f"Pick zone created! Now create the drop zone for '{process_name}'.\n\n"
            "Click OK and then use the zone creation tools to create the drop zone."
        )
        
        # Request drop zone creation
        drop_zone_name = f"Drop Zone {process_name.split()[-1]}"  # Extract number from "Process N"
        self.zone_creation_requested.emit("DROP", drop_zone_name)
    
    def on_drop_zone_created(self, zone_id: str, process_id: str, process_name: str):
        """Handle drop zone creation completion"""
        # Show completion message
        QMessageBox.information(
            self,
            "Process Created",
            f"Process '{process_name}' has been created successfully!\n\n"
            "You can now use the pick and drop zones for this process."
        )
        
        self.current_process_creation = None
    
    def clear_all_processes(self):
        """Clear all processes from the list"""
        self.process_list.processes.clear()
        self.process_list.refresh_list()