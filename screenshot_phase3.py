#!/usr/bin/env python3
"""
NextSight v2 Phase 3 - Zone Management Screenshot Demo
Creates a visual demonstration of the zone management system
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)


def create_zone_demo_screenshot():
    """Create a demonstration screenshot of the zone system"""
    
    # Try to import Qt modules
    try:
        from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
        from PyQt6.QtCore import Qt, QTimer
        from PyQt6.QtGui import QPixmap, QPainter, QPen, QBrush, QColor, QFont
    except ImportError as e:
        print(f"PyQt6 not available for screenshot demo: {e}")
        print("The zone management system is implemented and tested.")
        print("Run 'python demo_phase3.py' with a camera to see the full demo.")
        return
    
    app = QApplication(sys.argv)
    
    # Create main window
    window = QMainWindow()
    window.setWindowTitle("NextSight v2 - Zone Management Demo")
    window.setGeometry(100, 100, 900, 700)
    
    # Create central widget
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    layout = QVBoxLayout(central_widget)
    
    # Create demo canvas
    canvas = QLabel()
    canvas.setMinimumSize(800, 600)
    canvas.setStyleSheet("background-color: #2d2d30; border: 2px solid #007ACC;")
    layout.addWidget(canvas)
    
    # Create demo image
    demo_image = create_demo_image()
    canvas.setPixmap(demo_image)
    
    # Show window
    window.show()
    
    # Take screenshot after brief delay
    def take_screenshot():
        screenshot = window.grab()
        screenshot.save("nextsight_v2_phase3_screenshot.png")
        print("Screenshot saved: nextsight_v2_phase3_screenshot.png")
        app.quit()
    
    QTimer.singleShot(500, take_screenshot)
    
    return app.exec()


def create_demo_image():
    """Create a demo image showing zone management features"""
    from PyQt6.QtGui import QPixmap, QPainter, QPen, QBrush, QColor, QFont
    from PyQt6.QtCore import Qt
    
    # Create canvas
    pixmap = QPixmap(800, 600)
    pixmap.fill(QColor("#1e1e1e"))
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # Draw camera feed background
    camera_rect = (50, 50, 500, 375)  # 4:3 aspect ratio
    painter.setPen(QPen(QColor("#007ACC"), 2))
    painter.setBrush(QBrush(QColor("#000000")))
    painter.drawRect(*camera_rect)
    
    # Draw simulated hand landmarks
    draw_simulated_hands(painter, camera_rect)
    
    # Draw pick zone (green)
    pick_zone = (80, 150, 120, 80)
    painter.setPen(QPen(QColor("#00ff00"), 3))
    painter.setBrush(QBrush(QColor("#00ff00"), Qt.BrushStyle.Dense4Pattern))
    painter.drawRect(*pick_zone)
    
    # Pick zone label
    painter.setPen(QColor("#ffffff"))
    painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
    painter.drawText(85, 145, "PICK ZONE")
    painter.setFont(QFont("Arial", 8))
    painter.drawText(85, 245, "✓ Hand detected")
    
    # Draw drop zone (blue)
    drop_zone = (400, 200, 120, 80)
    painter.setPen(QPen(QColor("#0080ff"), 3))
    painter.setBrush(QBrush(QColor("#0080ff"), Qt.BrushStyle.Dense4Pattern))
    painter.drawRect(*drop_zone)
    
    # Drop zone label  
    painter.setPen(QColor("#ffffff"))
    painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
    painter.drawText(405, 195, "DROP ZONE")
    
    # Draw status information panel
    draw_status_panel(painter)
    
    # Draw zone creation preview
    preview_zone = (250, 100, 100, 60)
    painter.setPen(QPen(QColor("#ffaa00"), 2, Qt.PenStyle.DashLine))
    painter.setBrush(QBrush(QColor("#ffaa00")))
    painter.drawRect(*preview_zone)
    painter.setPen(QColor("#ffffff"))
    painter.setFont(QFont("Arial", 9))
    painter.drawText(255, 90, "Creating Zone...")
    
    # Draw title and info
    painter.setPen(QColor("#ffffff"))
    painter.setFont(QFont("Arial", 16, QFont.Weight.Bold))
    painter.drawText(50, 30, "NextSight v2 - Phase 3: Zone Management & Hand-Zone Interaction")
    
    painter.end()
    return pixmap


def draw_simulated_hands(painter, camera_rect):
    """Draw simulated hand landmarks"""
    from PyQt6.QtGui import QPen, QBrush, QColor
    from PyQt6.QtCore import Qt
    
    # Hand in pick zone
    hand1_points = [
        (120, 180), (125, 175), (130, 170), (135, 175), (140, 180),  # fingers
        (130, 190), (125, 195), (120, 200), (115, 195), (110, 190),  # palm
    ]
    
    painter.setPen(QPen(QColor("#00ff00"), 2))
    painter.setBrush(QBrush(QColor("#00ff00")))
    for x, y in hand1_points:
        painter.drawEllipse(x-2, y-2, 4, 4)
    
    # Draw hand connections
    for i in range(len(hand1_points)-1):
        x1, y1 = hand1_points[i]
        x2, y2 = hand1_points[i+1]
        painter.drawLine(x1, y1, x2, y2)
    
    # Hand moving towards drop zone  
    hand2_points = [
        (350, 220), (355, 215), (360, 210), (365, 215), (370, 220),
        (360, 230), (355, 235), (350, 240), (345, 235), (340, 230),
    ]
    
    painter.setPen(QPen(QColor("#ffaa00"), 2))
    painter.setBrush(QBrush(QColor("#ffaa00")))
    for x, y in hand2_points:
        painter.drawEllipse(x-2, y-2, 4, 4)


def draw_status_panel(painter):
    """Draw status information panel"""
    from PyQt6.QtGui import QPen, QBrush, QColor, QFont
    from PyQt6.QtCore import Qt
    
    # Status panel background
    status_rect = (580, 50, 180, 375)
    painter.setPen(QPen(QColor("#3e3e42"), 1))
    painter.setBrush(QBrush(QColor("#2d2d30")))
    painter.drawRect(*status_rect)
    
    # Status title
    painter.setPen(QColor("#ffffff"))
    painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
    painter.drawText(590, 75, "System Status")
    
    # Status items
    status_items = [
        ("Camera: Connected", "#00ff00"),
        ("Detection: Active", "#00ff00"),  
        ("Hands: 2", "#00ff00"),
        ("FPS: 28.5", "#00ff00"),
        ("", ""),
        ("Zones: 2/2", "#00ff00"),
        ("Active: 1", "#00ff00"),
        ("Picks: 3 ✓", "#00ff00"),
        ("Drops: 1", "#ffffff"),
        ("", ""),
        ("Zone Events:", "#ffffff"),
        ("• Hand entered", "#00ff00"),
        ("  Pick Zone", "#00ff00"),
        ("• Confidence: 0.87", "#ffffff"),
        ("• Duration: 2.3s", "#ffffff"),
    ]
    
    y_offset = 100
    painter.setFont(QFont("Arial", 9))
    for text, color in status_items:
        if text:
            painter.setPen(QColor(color))
            painter.drawText(590, y_offset, text)
        y_offset += 20
    
    # Controls info
    painter.setPen(QColor("#ffffff"))
    painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
    painter.drawText(590, 350, "Controls:")
    
    controls = [
        "Z - Toggle zones",
        "1 - Create pick zone", 
        "2 - Create drop zone",
        "Right-click - Menu"
    ]
    
    y_offset = 370
    painter.setFont(QFont("Arial", 8))
    for control in controls:
        painter.setPen(QColor("#cccccc"))
        painter.drawText(590, y_offset, control)
        y_offset += 15


def main():
    """Create zone management screenshot demo"""
    print("NextSight v2 Phase 3 - Creating Zone Management Screenshot Demo")
    print("=" * 65)
    
    try:
        return create_zone_demo_screenshot()
    except Exception as e:
        print(f"Error creating screenshot: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())