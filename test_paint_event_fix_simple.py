#!/usr/bin/env python3
"""
Simple code analysis test to verify the paintEvent fix for zone creation visual preview
Tests that doesn't require Qt imports to work in headless environment
"""

import sys
import os
import re

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_camera_widget_paint_event_code():
    """Test that CameraWidget source code has the paintEvent method"""
    print("Testing CameraWidget paintEvent implementation in source code...")
    
    try:
        with open('nextsight/ui/camera_widget.py', 'r') as f:
            source = f.read()
        
        # Check if paintEvent method is defined
        assert 'def paintEvent(self, event):' in source, "CameraWidget should have paintEvent method definition"
        
        # Check the method implementation contains required elements
        assert 'super().paintEvent(event)' in source, "paintEvent should call super().paintEvent(event)"
        assert 'zone_creator = self.zone_manager.get_zone_creator()' in source, "Should get zone creator from zone manager"
        assert 'zone_creator.is_creating' in source, "Should check if zone creator is creating"
        assert 'zone_creator.draw_preview(painter, widget_size)' in source, "Should call draw_preview"
        assert 'QPainter(self.camera_label)' in source, "Should create painter for camera label"
        assert 'painter.end()' in source, "Should properly end the painter"
        
        # Verify the paintEvent is properly indented (class method)
        lines = source.split('\n')
        paint_event_line = None
        for i, line in enumerate(lines):
            if 'def paintEvent(self, event):' in line:
                paint_event_line = i
                break
        
        assert paint_event_line is not None, "paintEvent method should be found"
        
        # Check indentation (should be a class method)
        paint_line = lines[paint_event_line]
        assert paint_line.startswith('    def '), "paintEvent should be properly indented as a class method"
        
        print("✓ CameraWidget paintEvent method is properly implemented in source code")
        return True
        
    except Exception as e:
        print(f"✗ Error testing CameraWidget paintEvent: {e}")
        return False

def test_zone_preview_update_code():
    """Test that zone preview update code triggers repaint"""
    print("Testing zone preview update repaint trigger in source code...")
    
    try:
        with open('nextsight/ui/camera_widget.py', 'r') as f:
            source = f.read()
        
        # Check if on_zone_preview_updated method calls update()
        assert 'def on_zone_preview_updated(self, preview_data):' in source, "CameraWidget should have on_zone_preview_updated method"
        assert 'self.update()' in source, "on_zone_preview_updated should call self.update() to trigger repaint"
        
        # Extract the method to verify it's properly structured
        lines = source.split('\n')
        method_start = None
        for i, line in enumerate(lines):
            if 'def on_zone_preview_updated(self, preview_data):' in line:
                method_start = i
                break
        
        assert method_start is not None, "on_zone_preview_updated method should be found"
        
        # Check a few lines after the method definition
        method_lines = lines[method_start:method_start+10]
        method_content = '\n'.join(method_lines)
        
        assert 'self.update()' in method_content, "self.update() should be in the method"
        
        print("✓ Zone preview update properly triggers repaint in source code")
        return True
        
    except Exception as e:
        print(f"✗ Error testing zone preview update: {e}")
        return False

def test_zone_creator_draw_preview_code():
    """Test that ZoneCreator has the draw_preview method"""
    print("Testing ZoneCreator draw_preview method in source code...")
    
    try:
        with open('nextsight/zones/zone_creator.py', 'r') as f:
            source = f.read()
        
        # Check if draw_preview method exists
        assert 'def draw_preview(self, painter: QPainter, widget_size: Tuple[int, int]):' in source, "ZoneCreator should have draw_preview method"
        
        # Check that it has proper implementation
        assert 'painter.drawRect' in source, "draw_preview should call painter.drawRect"
        assert 'preview_rect = self._get_preview_rectangle()' in source, "Should get preview rectangle"
        
        print("✓ ZoneCreator draw_preview method is available in source code")
        return True
        
    except Exception as e:
        print(f"✗ Error testing ZoneCreator draw_preview: {e}")
        return False

def test_missing_duplicate_mouse_press_event():
    """Test that there's no duplicate mousePressEvent methods causing conflicts"""
    print("Testing for duplicate mousePressEvent methods...")
    
    try:
        with open('nextsight/ui/camera_widget.py', 'r') as f:
            source = f.read()
        
        # Count occurrences of mousePressEvent method definitions
        method_pattern = r'def mousePressEvent\(self, event'
        matches = re.findall(method_pattern, source)
        
        # There should be exactly one mousePressEvent method
        assert len(matches) == 1, f"Expected exactly 1 mousePressEvent method, found {len(matches)}"
        
        print("✓ No duplicate mousePressEvent methods found")
        return True
        
    except Exception as e:
        print(f"✗ Error checking for duplicate methods: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing paintEvent fix for zone creation visual preview (code analysis)")
    print("=" * 70)
    
    tests = [
        test_camera_widget_paint_event_code,
        test_zone_preview_update_code,
        test_zone_creator_draw_preview_code,
        test_missing_duplicate_mouse_press_event,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
            print()
    
    print("=" * 70)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All tests passed! The paintEvent fix appears to be properly implemented.")
        return True
    else:
        print("✗ Some tests failed. Please review the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)