# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for NextSight v2 Application
Builds a standalone executable with all dependencies included.
"""

import sys
import os
from pathlib import Path

# Get the application directory
app_dir = Path(SPECPATH)

# Define the main script
main_script = str(app_dir / 'main.py')

# Additional data files that need to be included
added_files = [
    # Include zones configuration
    (str(app_dir / 'zones.json'), '.'),
]

# Hidden imports for dynamic loading and complex dependencies
hidden_imports = [
    # Core nextsight modules
    'nextsight',
    'nextsight.core',
    'nextsight.core.application',
    'nextsight.core.window',
    'nextsight.core.camera_thread',
    'nextsight.ui',
    'nextsight.utils',
    'nextsight.vision',
    'nextsight.zones',
    
    # PyQt6 modules
    'PyQt6',
    'PyQt6.QtCore',
    'PyQt6.QtGui', 
    'PyQt6.QtWidgets',
    'PyQt6.QtOpenGL',
    'PyQt6.QtOpenGLWidgets',
    
    # OpenCV and computer vision
    'cv2',
    'numpy',
    'PIL',
    'PIL.Image',
    
    # MediaPipe and dependencies
    'mediapipe',
    'mediapipe.python',
    'mediapipe.framework',
    'mediapipe.python.solutions',
    'mediapipe.python.solutions.hands',
    'mediapipe.python.solutions.drawing_utils',
    'mediapipe.python.solutions.drawing_styles',
    
    # Common hidden imports for GUI applications
    'pkg_resources.py2_warn',
    'pkg_resources.markers',
]

# Excluded modules to reduce size
excludes = [
    'matplotlib',
    'scipy.spatial.distance',
    'scipy.sparse',
    'IPython',
    'jupyter',
    'notebook',
    'tkinter',
]

# Binary excludes to reduce size
binaries_excludes = []

# PyInstaller Analysis
a = Analysis(
    [main_script],
    pathex=[str(app_dir)],
    binaries=[],
    datas=added_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Remove duplicate binaries and optimize
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Executable configuration
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='NextSight-v2',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True for debugging, False for release
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add path to .ico file here if you have an icon
)

# Additional configuration for different platforms
if sys.platform == 'win32':
    exe.version_info = {
        'FileDescription': 'NextSight v2 - Professional Computer Vision Exhibition Demo',
        'ProductName': 'NextSight v2',
        'ProductVersion': '2.0.0',
        'FileVersion': '2.0.0',
        'CompanyName': 'NextSight',
        'LegalCopyright': 'Copyright (c) 2024 NextSight',
    }