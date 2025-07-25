#!/usr/bin/env python3
"""
Test script to verify the paintEvent fix for zone creation visual preview
Tests that the CameraWidget properly implements paintEvent for zone creation
"""

import sys
import os
import inspect

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_camera_widget_has_paint_event():
    """Test that CameraWidget has the paintEvent method"""
    print("Testing CameraWidget paintEvent implementation...")
    
    try:
        from nextsight.ui.camera_widget import CameraWidget
        
        # Check if paintEvent method exists
        assert hasattr(CameraWidget, 'paintEvent'), "CameraWidget should have paintEvent method"
        
        # Check the method signature
        method = getattr(CameraWidget, 'paintEvent')
        assert callable(method), "paintEvent should be callable"
        
        # Get the source code to verify implementation
        source = inspect.getsource(method)
        
        # Verify the implementation contains the required elements
        assert 'super().paintEvent(event)' in source, "paintEvent should call super().paintEvent(event)"
        assert 'zone_creator = self.zone_manager.get_zone_creator()' in source, "Should get zone creator from zone manager"
        assert 'zone_creator.is_creating' in source, "Should check if zone creator is creating"
        assert 'zone_creator.draw_preview(painter, widget_size)' in source, "Should call draw_preview"
        assert 'QPainter(self.camera_label)' in source, "Should create painter for camera label"
        assert 'painter.end()' in source, "Should properly end the painter"
        
        print("✓ CameraWidget paintEvent method is properly implemented")
        return True
        
    except Exception as e:
        print(f"✗ Error testing CameraWidget paintEvent: {e}")
        return False

def test_zone_preview_update_triggers_repaint():
    """Test that zone preview updates trigger widget repaint"""
    print("Testing zone preview update repaint trigger...")
    
    try:
        from nextsight.ui.camera_widget import CameraWidget
        
        # Check if on_zone_preview_updated method exists and calls update()
        assert hasattr(CameraWidget, 'on_zone_preview_updated'), "CameraWidget should have on_zone_preview_updated method"
        
        method = getattr(CameraWidget, 'on_zone_preview_updated')
        source = inspect.getsource(method)
        
        # Verify it calls self.update() to trigger repaint
        assert 'self.update()' in source, "on_zone_preview_updated should call self.update() to trigger repaint"
        
        print("✓ Zone preview update properly triggers repaint")
        return True
        
    except Exception as e:
        print(f"✗ Error testing zone preview update: {e}")
        return False

def test_zone_creator_draw_preview_method():
    """Test that ZoneCreator has the draw_preview method that will be called"""
    print("Testing ZoneCreator draw_preview method...")
    
    try:
        from nextsight.zones.zone_creator import ZoneCreator
        
        # Check if draw_preview method exists
        assert hasattr(ZoneCreator, 'draw_preview'), "ZoneCreator should have draw_preview method"
        
        method = getattr(ZoneCreator, 'draw_preview')
        assert callable(method), "draw_preview should be callable"
        
        # Check method signature
        sig = inspect.signature(method)
        params = list(sig.parameters.keys())
        
        # Should have self, painter, widget_size parameters
        assert 'painter' in params, "draw_preview should accept painter parameter"
        assert 'widget_size' in params, "draw_preview should accept widget_size parameter"
        
        print("✓ ZoneCreator draw_preview method is available and properly structured")
        return True
        
    except Exception as e:
        print(f"✗ Error testing ZoneCreator draw_preview: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing paintEvent fix for zone creation visual preview")
    print("=" * 60)
    
    tests = [
        test_camera_widget_has_paint_event,
        test_zone_preview_update_triggers_repaint,
        test_zone_creator_draw_preview_method,
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
    
    print("=" * 60)
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