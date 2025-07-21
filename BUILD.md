# NextSight v2 - Build Documentation

This document provides comprehensive instructions for building NextSight v2 into a standalone executable.

## Overview

NextSight v2 uses PyInstaller to create standalone executables that include all necessary dependencies. The resulting executable can run on any compatible system without requiring Python or any external libraries to be installed.

## Build Requirements

### System Requirements
- Python 3.8 or higher
- 4GB+ RAM (for build process)
- 2GB+ free disk space
- Operating System:
  - Windows 10/11 (x64)
  - Linux (x64) - Ubuntu 18.04+ or equivalent
  - macOS 10.14+ (x64 or Apple Silicon)

### Python Dependencies
All dependencies are automatically installed via requirements.txt:
```
PyQt6==6.7.1           # GUI framework
opencv-python==4.10.0.84   # Computer vision
mediapipe==0.10.14      # Hand detection models  
numpy==1.26.4           # Numerical computing
Pillow==10.4.0          # Image processing
pyinstaller==6.11.1    # Executable builder
```

## Build Methods

### Method 1: Automated Build Scripts (Recommended)

#### Windows
```batch
# Run the Windows build script
build.bat
```

The script will:
1. Install/update all dependencies
2. Clean previous build artifacts
3. Build the executable using PyInstaller
4. Verify the output
5. Display build information

#### Cross-Platform
```bash
# Make script executable (Linux/macOS)
chmod +x build.sh

# Run the build script
./build.sh
```

### Method 2: Manual Build Process

#### Step 1: Install Dependencies
```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt
```

#### Step 2: Clean Previous Builds (Optional)
```bash
# Remove old build artifacts
rm -rf build/ dist/ __pycache__/
```

#### Step 3: Build Executable
```bash
# Build using the spec file
pyinstaller --clean nextsight.spec
```

#### Step 4: Verify Output
Check the `dist/` directory for your executable:
- Windows: `NextSight-v2.exe`
- Linux/macOS: `NextSight-v2`

## Build Configuration

### PyInstaller Spec File (`nextsight.spec`)

The build is configured through a comprehensive spec file that handles:

#### Included Dependencies
- **Core Application**: All nextsight modules
- **GUI Framework**: Complete PyQt6 framework
- **Computer Vision**: OpenCV with all modules
- **Machine Learning**: MediaPipe with pre-trained models
- **Numerical**: NumPy with optimized libraries
- **Image Processing**: Pillow with format support

#### Data Files
- `zones.json` - Zone configuration file
- MediaPipe model files (automatically detected)
- Qt platform plugins and libraries

#### Optimizations
- **Single File**: Everything bundled into one executable
- **UPX Compression**: Reduced file size (Linux/macOS only)
- **Import Optimization**: Only necessary modules included
- **Binary Exclusion**: Unnecessary libraries removed

#### Platform-Specific Features

##### Windows
- Version information metadata
- No console window (windowed application)
- .exe file extension
- Windows-specific Qt plugins

##### Linux/macOS
- Executable permissions set automatically
- Platform-specific Qt libraries
- Shared library dependencies resolved

## Build Output

### File Information
- **Size**: Approximately 275-300 MB
- **Type**: Single-file executable
- **Dependencies**: Self-contained (no external requirements)
- **Architecture**: Matches build platform

### Distribution
The generated executable can be:
- Copied to any compatible system
- Run without Python installation
- Distributed via any standard method
- Deployed in enterprise environments

## Troubleshooting

### Common Issues

#### 1. Missing Dependencies
**Problem**: Build fails with import errors
**Solution**: 
```bash
pip install -r requirements.txt --upgrade
```

#### 2. Insufficient Memory
**Problem**: Build process runs out of memory
**Solution**: 
- Close other applications
- Increase virtual memory/swap
- Use a machine with more RAM

#### 3. Permission Errors
**Problem**: Cannot write to build directories
**Solution**:
```bash
# Windows (run as administrator)
# Linux/macOS
sudo ./build.sh
```

#### 4. Qt Library Warnings
**Problem**: Warnings about missing X11 libraries (Linux)
**Solution**: These warnings are normal in headless environments and don't affect functionality.

### Platform-Specific Notes

#### Windows
- Build on Windows for Windows targets
- Antivirus may flag the executable (false positive)
- UAC prompt may appear for unsigned executables

#### Linux
- Install system Qt dependencies if needed:
  ```bash
  # Ubuntu/Debian
  sudo apt-get install qt6-base-dev
  
  # CentOS/RHEL
  sudo yum install qt6-qtbase-devel
  ```

#### macOS
- Code signing may be required for distribution
- Gatekeeper may block unsigned executables
- Build on macOS for macOS targets

## Customization

### Icon and Metadata
To add a custom icon:
1. Add your icon file (`.ico` for Windows, `.icns` for macOS)
2. Update the `icon` parameter in `nextsight.spec`
3. Rebuild the executable

### Excluding Modules
To reduce file size by excluding unnecessary modules:
1. Add module names to the `excludes` list in `nextsight.spec`
2. Test thoroughly to ensure functionality
3. Rebuild and verify

### Including Additional Files
To include extra data files:
1. Add file paths to the `added_files` list in `nextsight.spec`
2. Update the destination path as needed
3. Rebuild the executable

## Performance Considerations

### Build Time
- Initial build: 5-15 minutes (depending on system)
- Incremental builds: 2-5 minutes (with `--clean`)
- Parallel processing: Automatically used when available

### Runtime Performance
- Startup time: 3-10 seconds (first run may be slower)
- Memory usage: Similar to Python version
- CPU usage: Identical to Python version
- Disk space: Self-contained, no additional space needed

## Security Considerations

### Code Protection
- Python source code is compiled to bytecode
- Not fully obfuscated (reverse engineering possible)
- Consider additional protection for sensitive applications

### Distribution Security
- Sign executables for production distribution
- Verify integrity with checksums
- Use secure distribution channels

## Automation

### CI/CD Integration
The build scripts can be integrated into automated pipelines:

```yaml
# Example GitHub Actions workflow
name: Build Executable
on: [push, release]
jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [windows-latest, ubuntu-latest, macos-latest]
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: pyinstaller --clean nextsight.spec
      - uses: actions/upload-artifact@v2
        with:
          name: nextsight-${{ matrix.os }}
          path: dist/
```

## Support

For build-related issues:
1. Check this documentation
2. Verify system requirements
3. Test with a clean Python environment
4. Check PyInstaller logs in `build/` directory
5. Consult PyInstaller documentation for advanced issues