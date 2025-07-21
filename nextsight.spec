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
    
    # MediaPipe model files and data
    # Note: The following paths will be resolved at build time
]

# Add MediaPipe model files dynamically
try:
    import mediapipe as mp
    import os
    mp_path = os.path.dirname(mp.__file__)
    
    # Add MediaPipe modules directory (contains .tflite model files)
    modules_path = os.path.join(mp_path, 'modules')
    if os.path.exists(modules_path):
        added_files.append((modules_path, 'mediapipe/modules'))
    
    # Add MediaPipe python directory
    python_path = os.path.join(mp_path, 'python')
    if os.path.exists(python_path):
        added_files.append((python_path, 'mediapipe/python'))
        
except ImportError:
    print("Warning: MediaPipe not found during spec evaluation")
    pass

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
    
    # MediaPipe and all its dependencies
    'mediapipe',
    'mediapipe.python',
    'mediapipe.framework',
    'mediapipe.python.solutions',
    'mediapipe.python.solutions.hands',
    'mediapipe.python.solutions.drawing_utils',
    'mediapipe.python.solutions.drawing_styles',
    
    # MediaPipe required dependencies
    'matplotlib',
    'matplotlib.pyplot',
    'matplotlib.backends',
    'matplotlib.backends.backend_agg',
    'protobuf',
    'google.protobuf',
    'google.protobuf.internal',
    'attrs',
    'absl',
    'absl.flags',
    'absl.logging',
    'flatbuffers',
    'sounddevice',
    
    # JAX dependencies (required by MediaPipe)
    'jax',
    'jaxlib',
    'opt_einsum',
    'ml_dtypes',
    
    # Scientific computing
    'scipy',
    'scipy.spatial',
    'scipy.spatial.distance',
    
    # Common hidden imports for GUI applications
    'pkg_resources.py2_warn',
    'pkg_resources.markers',
]

# Excluded modules to reduce size (only exclude what's truly not needed)
excludes = [
    'IPython',
    'jupyter',
    'notebook',
    'tkinter',
    'test',
    'tests',
    'unittest',
    'pytest',
    'doctest',
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