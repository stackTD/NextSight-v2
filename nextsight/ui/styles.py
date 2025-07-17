"""
Professional dark theme styling for NextSight v2
"""

# Main application dark theme
DARK_THEME = """
QMainWindow {
    background-color: #1e1e1e;
    color: #ffffff;
}

QWidget {
    background-color: #1e1e1e;
    color: #ffffff;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 10pt;
}

/* Custom Title Bar */
QWidget#titleBar {
    background-color: #2d2d30;
    border: none;
    height: 40px;
}

QLabel#titleLabel {
    color: #ffffff;
    font-size: 12pt;
    font-weight: bold;
    padding-left: 15px;
}

QPushButton#titleButton {
    background-color: transparent;
    border: none;
    color: #ffffff;
    font-size: 10pt;
    padding: 8px 15px;
    min-width: 40px;
    max-width: 40px;
}

QPushButton#titleButton:hover {
    background-color: #3e3e42;
}

QPushButton#closeButton:hover {
    background-color: #e53e3e;
}

/* Main panels */
QWidget#cameraPanel {
    background-color: #252526;
    border: 2px solid #3e3e42;
    border-radius: 8px;
    margin: 5px;
}

QWidget#controlPanel {
    background-color: #2d2d30;
    border: 1px solid #3e3e42;
    border-radius: 8px;
    margin: 5px;
    padding: 10px;
}

/* Camera display */
QLabel#cameraDisplay {
    background-color: #000000;
    border: 2px solid #007ACC;
    border-radius: 6px;
    margin: 10px;
}

/* Status bar */
QStatusBar {
    background-color: #007ACC;
    color: #ffffff;
    border: none;
    padding: 5px;
}

QStatusBar::item {
    border: none;
}

/* Control buttons */
QPushButton {
    background-color: #0078d4;
    border: none;
    border-radius: 4px;
    color: #ffffff;
    font-weight: bold;
    padding: 8px 16px;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #106ebe;
}

QPushButton:pressed {
    background-color: #005a9e;
}

QPushButton:disabled {
    background-color: #3e3e42;
    color: #888888;
}

/* Toggle buttons */
QPushButton#toggleButton {
    background-color: #2d2d30;
    border: 2px solid #007ACC;
}

QPushButton#toggleButton:checked {
    background-color: #007ACC;
    border: 2px solid #0078d4;
}

/* Labels */
QLabel {
    color: #ffffff;
    font-size: 10pt;
}

QLabel#statusLabel {
    color: #00ff00;
    font-weight: bold;
}

QLabel#errorLabel {
    color: #ff6b6b;
    font-weight: bold;
}

/* Scroll areas */
QScrollArea {
    border: 1px solid #3e3e42;
    border-radius: 4px;
    background-color: #252526;
}

QScrollBar:vertical {
    background-color: #2d2d30;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #007ACC;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #0078d4;
}

/* Group boxes */
QGroupBox {
    font-weight: bold;
    border: 2px solid #3e3e42;
    border-radius: 5px;
    margin-top: 10px;
    padding-top: 10px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px 0 5px;
    color: #007ACC;
}

/* Sliders */
QSlider::groove:horizontal {
    border: 1px solid #3e3e42;
    height: 8px;
    background: #2d2d30;
    border-radius: 4px;
}

QSlider::handle:horizontal {
    background: #007ACC;
    border: 1px solid #0078d4;
    width: 18px;
    border-radius: 9px;
    margin: -5px 0;
}

QSlider::handle:horizontal:hover {
    background: #0078d4;
}

/* Checkboxes */
QCheckBox {
    spacing: 8px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 2px solid #3e3e42;
    border-radius: 3px;
    background-color: #2d2d30;
}

QCheckBox::indicator:checked {
    background-color: #007ACC;
    border-color: #0078d4;
}

QCheckBox::indicator:checked::before {
    content: "✓";
    color: white;
    font-weight: bold;
}
"""

def apply_dark_theme(app):
    """Apply the dark theme to the application"""
    app.setStyleSheet(DARK_THEME)