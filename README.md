# NextSight v2 - Professional Computer Vision Exhibition Demo

A professional PyQt6-based computer vision platform featuring real-time hand detection with MediaPipe integration, designed for exhibition demonstrations.

## Features

### 🎨 Professional Interface
- Custom title bar with NextSight branding
- Professional dark theme styling
- Responsive layout that adapts to different screen sizes
- Modern UI controls with hover effects

### 📹 Camera Integration
- Real-time camera feed with OpenCV
- Threaded operations for smooth performance
- Support for multiple cameras
- Camera resolution optimization (default: 1280x720)

### 🤚 Hand Detection
- MediaPipe-powered hand landmark detection
- Real-time visualization with 21 hand landmarks
- Configurable detection confidence thresholds
- Hand type identification (Left/Right)
- Connection lines between landmarks

### ⚡ Performance
- Optimized for 30+ FPS on modern hardware
- Non-blocking threaded camera operations
- Real-time performance monitoring
- Memory-efficient processing

## Installation

### Prerequisites
- Python 3.8 or higher
- Webcam or compatible camera device

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Dependencies
- PyQt6 6.7.1 - Modern GUI framework
- OpenCV 4.10.0 - Computer vision library
- MediaPipe 0.10.14 - Hand detection ML models
- NumPy 1.26.4 - Numerical computing
- Pillow 10.4.0 - Image processing
- PyInstaller 6.11.1 - Standalone executable builder

## Building Standalone Executable

### Overview
NextSight v2 can be built into a standalone executable file that doesn't require Python installation on the target machine. This is perfect for distribution and deployment.

### Quick Build

#### Windows
```batch
build.bat
```

#### Cross-Platform (Linux, macOS, Windows with Git Bash)
```bash
./build.sh
```

### Manual Build Process
If you prefer to build manually:

1. **Install Build Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Build Executable**
   ```bash
   pyinstaller --clean nextsight.spec
   ```

3. **Locate Output**
   The executable will be created in the `dist/` directory:
   - Windows: `dist/NextSight-v2.exe`
   - Linux/macOS: `dist/NextSight-v2`

### Build Configuration
The build process is configured via `nextsight.spec` which includes:
- Single-file executable generation
- All necessary dependencies bundled
- Optimized for distribution (UPX compression)
- Windows version information metadata
- Proper handling of MediaPipe and OpenCV data files

### Build Output
- **File Size**: ~275-300 MB (includes all dependencies)
- **Architecture**: Matches build platform (x64 recommended)
- **Dependencies**: All Python libraries and Qt frameworks included
- **Standalone**: No Python installation required on target system

## Usage

### Run the Application
```bash
python main.py
```

### Controls
- **Detection Toggle**: Enable/disable hand detection
- **Landmarks**: Show/hide hand landmark points
- **Connections**: Show/hide connection lines between landmarks
- **Confidence Slider**: Adjust detection sensitivity
- **Camera Switch**: Toggle between available cameras

### Testing
Run the comprehensive test suite:
```bash
python test_phase1.py
```

Generate a visual demonstration:
```bash
python demo_screenshot.py
```

## Architecture

```
nextsight/
├── core/                   # Core application logic
│   ├── application.py      # Main application class
│   ├── window.py          # Custom window with title bar
│   └── camera_thread.py   # Threaded camera operations
├── ui/                     # User interface components  
│   ├── main_widget.py     # Central layout with controls
│   ├── camera_widget.py   # Video display with overlays
│   ├── status_bar.py      # Performance status bar
│   └── styles.py          # Professional dark theme
├── vision/                 # Computer vision modules
│   └── detector.py        # MediaPipe hand detection
└── utils/                  # Configuration and utilities
    └── config.py          # Application settings
```

## Configuration

Edit `nextsight/utils/config.py` to customize:
- Camera resolution and FPS
- Hand detection parameters
- UI window dimensions
- Performance settings

## Phase 1 Status: ✅ Complete

All Phase 1 requirements have been successfully implemented:
- ✅ Professional PyQt6 foundation
- ✅ Camera integration with threading
- ✅ MediaPipe hand detection
- ✅ Professional UI layout
- ✅ Performance optimization
- ✅ Comprehensive testing

## Requirements Met

### Technical Specifications
- **Framework**: PyQt6 ✅
- **Computer Vision**: OpenCV + MediaPipe ✅
- **Threading**: QThread for camera operations ✅
- **Styling**: Custom QSS stylesheets ✅
- **Target Performance**: 30+ FPS capable ✅

### Success Criteria
- ✅ Professional exhibition-ready window appearance
- ✅ Smooth real-time camera feed display
- ✅ Basic hand detection working with visual overlay
- ✅ Responsive UI with proper threading
- ✅ Solid foundation for Phase 2 development

## Next Steps (Phase 2)
- Object Pick/Drop detection
- Advanced gesture recognition
- Enhanced computer vision features
- Exhibition-specific optimizations

## License
Copyright © 2024 NextSight Team