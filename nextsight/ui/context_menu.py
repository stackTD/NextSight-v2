"""
Context menu for zone management in NextSight v2
Right-click menu for zone operations and properties
"""

from PyQt6.QtWidgets import (QMenu, QAction, QDialog, QVBoxLayout, QHBoxLayout,
                           QLabel, QLineEdit, QComboBox, QSlider, QSpinBox,
                           QPushButton, QColorDialog, QGroupBox, QFormLayout,
                           QCheckBox, QDialogButtonBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPixmap, QPainter
from typing import Optional, Callable
from nextsight.zones.zone_config import Zone, ZoneType


class ZonePropertiesDialog(QDialog):
    """Dialog for editing zone properties"""
    
    def __init__(self, zone: Zone, parent=None):
        super().__init__(parent)
        self.zone = zone.copy() if hasattr(zone, 'copy') else Zone(
            id=zone.id, name=zone.name, zone_type=zone.zone_type,
            x=zone.x, y=zone.y, width=zone.width, height=zone.height,
            active=zone.active, confidence_threshold=zone.confidence_threshold,
            color=zone.color, alpha=zone.alpha, border_width=zone.border_width
        )
        
        self.setWindowTitle(f"Zone Properties - {zone.name}")
        self.setFixedSize(400, 500)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the properties dialog UI"""
        layout = QVBoxLayout(self)
        
        # Basic properties group
        basic_group = QGroupBox("Basic Properties")
        basic_layout = QFormLayout(basic_group)
        
        # Zone name
        self.name_edit = QLineEdit(self.zone.name)
        basic_layout.addRow("Name:", self.name_edit)
        
        # Zone type
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Pick", "Drop"])
        self.type_combo.setCurrentText(self.zone.zone_type.value.title())
        basic_layout.addRow("Type:", self.type_combo)
        
        # Active checkbox
        self.active_check = QCheckBox()
        self.active_check.setChecked(self.zone.active)
        basic_layout.addRow("Active:", self.active_check)
        
        layout.addWidget(basic_group)
        
        # Geometry group
        geom_group = QGroupBox("Geometry (Normalized 0-1)")
        geom_layout = QFormLayout(geom_group)
        
        # Position and size
        self.x_spin = self._create_double_spinbox(self.zone.x, 0.0, 1.0, 0.01)
        self.y_spin = self._create_double_spinbox(self.zone.y, 0.0, 1.0, 0.01)
        self.width_spin = self._create_double_spinbox(self.zone.width, 0.01, 1.0, 0.01)
        self.height_spin = self._create_double_spinbox(self.zone.height, 0.01, 1.0, 0.01)
        
        geom_layout.addRow("X:", self.x_spin)
        geom_layout.addRow("Y:", self.y_spin)
        geom_layout.addRow("Width:", self.width_spin)
        geom_layout.addRow("Height:", self.height_spin)
        
        layout.addWidget(geom_group)
        
        # Visual properties group
        visual_group = QGroupBox("Visual Properties")
        visual_layout = QFormLayout(visual_group)
        
        # Color picker
        self.color_button = QPushButton()
        self.color_button.setFixedSize(60, 30)
        self.color_button.clicked.connect(self.choose_color)
        self.update_color_button()
        visual_layout.addRow("Color:", self.color_button)
        
        # Alpha slider
        self.alpha_slider = QSlider(Qt.Orientation.Horizontal)
        self.alpha_slider.setRange(0, 100)
        self.alpha_slider.setValue(int(self.zone.alpha * 100))
        self.alpha_label = QLabel(f"{int(self.zone.alpha * 100)}%")
        self.alpha_slider.valueChanged.connect(
            lambda v: self.alpha_label.setText(f"{v}%")
        )
        
        alpha_layout = QHBoxLayout()
        alpha_layout.addWidget(self.alpha_slider)
        alpha_layout.addWidget(self.alpha_label)
        visual_layout.addRow("Transparency:", alpha_layout)
        
        # Border width
        self.border_spin = QSpinBox()
        self.border_spin.setRange(1, 10)
        self.border_spin.setValue(self.zone.border_width)
        visual_layout.addRow("Border Width:", self.border_spin)
        
        layout.addWidget(visual_group)
        
        # Detection properties group
        detection_group = QGroupBox("Detection Properties")
        detection_layout = QFormLayout(detection_group)
        
        # Confidence threshold
        self.confidence_slider = QSlider(Qt.Orientation.Horizontal)
        self.confidence_slider.setRange(10, 100)
        self.confidence_slider.setValue(int(self.zone.confidence_threshold * 100))
        self.confidence_label = QLabel(f"{self.zone.confidence_threshold:.2f}")
        self.confidence_slider.valueChanged.connect(
            lambda v: self.confidence_label.setText(f"{v/100:.2f}")
        )
        
        conf_layout = QHBoxLayout()
        conf_layout.addWidget(self.confidence_slider)
        conf_layout.addWidget(self.confidence_label)
        detection_layout.addRow("Confidence Threshold:", conf_layout)
        
        layout.addWidget(detection_group)
        
        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def _create_double_spinbox(self, value: float, min_val: float, max_val: float, step: float):
        """Create a double spinbox with given parameters"""
        spinbox = QSpinBox()
        # Simulate double spinbox with integer values (multiply by 100)
        spinbox.setRange(int(min_val * 100), int(max_val * 100))
        spinbox.setValue(int(value * 100))
        spinbox.setSuffix(" %")
        return spinbox
    
    def choose_color(self):
        """Open color picker dialog"""
        current_color = QColor(self.zone.color)
        color = QColorDialog.getColor(current_color, self, "Choose Zone Color")
        
        if color.isValid():
            self.zone.color = color.name()
            self.update_color_button()
    
    def update_color_button(self):
        """Update color button appearance"""
        color = QColor(self.zone.color)
        pixmap = QPixmap(50, 20)
        pixmap.fill(color)
        
        # Add border
        painter = QPainter(pixmap)
        painter.setPen(QColor("#000000"))
        painter.drawRect(0, 0, 49, 19)
        painter.end()
        
        self.color_button.setIcon(pixmap)
        self.color_button.setText(self.zone.color)
    
    def get_zone_properties(self) -> dict:
        """Get updated zone properties from dialog"""
        return {
            'name': self.name_edit.text(),
            'zone_type': ZoneType.PICK if self.type_combo.currentText() == "Pick" else ZoneType.DROP,
            'active': self.active_check.isChecked(),
            'x': self.x_spin.value() / 100.0,
            'y': self.y_spin.value() / 100.0,
            'width': self.width_spin.value() / 100.0,
            'height': self.height_spin.value() / 100.0,
            'color': self.zone.color,
            'alpha': self.alpha_slider.value() / 100.0,
            'border_width': self.border_spin.value(),
            'confidence_threshold': self.confidence_slider.value() / 100.0
        }


class ZoneContextMenu(QMenu):
    """Context menu for zone operations"""
    
    # Signals
    create_pick_zone_requested = pyqtSignal()
    create_drop_zone_requested = pyqtSignal()
    edit_zone_requested = pyqtSignal(str)  # zone_id
    delete_zone_requested = pyqtSignal(str)  # zone_id
    toggle_zone_active_requested = pyqtSignal(str)  # zone_id
    clear_all_zones_requested = pyqtSignal()
    save_zones_requested = pyqtSignal()
    load_zones_requested = pyqtSignal()
    
    def __init__(self, zone: Optional[Zone] = None, parent=None):
        super().__init__(parent)
        self.zone = zone
        self.setup_menu()
    
    def setup_menu(self):
        """Setup context menu items"""
        if self.zone:
            # Zone-specific actions
            self.setup_zone_menu()
        else:
            # General actions
            self.setup_general_menu()
    
    def setup_zone_menu(self):
        """Setup menu for specific zone"""
        zone = self.zone
        
        # Zone info header
        info_action = QAction(f"{zone.name} ({zone.zone_type.value.title()})", self)
        info_action.setEnabled(False)
        self.addAction(info_action)
        self.addSeparator()
        
        # Edit zone
        edit_action = QAction("Edit Properties...", self)
        edit_action.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_FileDialogDetailView))
        edit_action.triggered.connect(lambda: self.edit_zone_requested.emit(zone.id))
        self.addAction(edit_action)
        
        # Toggle active state
        toggle_text = "Deactivate" if zone.active else "Activate"
        toggle_action = QAction(toggle_text, self)
        toggle_action.triggered.connect(lambda: self.toggle_zone_active_requested.emit(zone.id))
        self.addAction(toggle_action)
        
        self.addSeparator()
        
        # Delete zone
        delete_action = QAction("Delete Zone", self)
        delete_action.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_DialogCancelButton))
        delete_action.triggered.connect(lambda: self.delete_zone_requested.emit(zone.id))
        self.addAction(delete_action)
        
        self.addSeparator()
        
        # Zone statistics
        if hasattr(zone, 'interaction_count'):
            stats_text = f"Interactions: {zone.interaction_count}"
            if zone.hands_inside:
                stats_text += f" | Hands: {len(zone.hands_inside)}"
            
            stats_action = QAction(stats_text, self)
            stats_action.setEnabled(False)
            self.addAction(stats_action)
    
    def setup_general_menu(self):
        """Setup general zone management menu"""
        # Create zone submenu
        create_menu = self.addMenu("Create Zone")
        create_menu.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_FileDialogNewFolder))
        
        # Pick zone
        pick_action = QAction("Pick Zone", create_menu)
        pick_action.setStatusTip("Create a new pick zone")
        pick_action.triggered.connect(self.create_pick_zone_requested.emit)
        create_menu.addAction(pick_action)
        
        # Drop zone
        drop_action = QAction("Drop Zone", create_menu)
        drop_action.setStatusTip("Create a new drop zone")
        drop_action.triggered.connect(self.create_drop_zone_requested.emit)
        create_menu.addAction(drop_action)
        
        self.addSeparator()
        
        # Zone management actions
        save_action = QAction("Save Zones", self)
        save_action.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_DialogSaveButton))
        save_action.triggered.connect(self.save_zones_requested.emit)
        self.addAction(save_action)
        
        load_action = QAction("Load Zones", self)
        load_action.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_DialogOpenButton))
        load_action.triggered.connect(self.load_zones_requested.emit)
        self.addAction(load_action)
        
        self.addSeparator()
        
        # Clear all zones
        clear_action = QAction("Clear All Zones", self)
        clear_action.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_DialogResetButton))
        clear_action.triggered.connect(self.clear_all_zones_requested.emit)
        self.addAction(clear_action)


def show_zone_properties_dialog(zone: Zone, parent=None) -> Optional[dict]:
    """Show zone properties dialog and return updated properties"""
    dialog = ZonePropertiesDialog(zone, parent)
    
    if dialog.exec() == QDialog.DialogCode.Accepted:
        return dialog.get_zone_properties()
    
    return None


def show_zone_context_menu(position, zone: Optional[Zone] = None, parent=None) -> ZoneContextMenu:
    """Show zone context menu at position"""
    menu = ZoneContextMenu(zone, parent)
    menu.exec(position)
    return menu