#!/bin/bash
# Build script for NextSight v2 executable
# This script builds a standalone executable using PyInstaller
# Compatible with Linux, macOS, and Windows (via Git Bash/WSL)

set -e  # Exit on any error

echo "============================================"
echo "NextSight v2 - Build Script (Cross-Platform)"
echo "============================================"
echo

# Function to print colored output
print_status() {
    echo -e "\e[32m$1\e[0m"
}

print_error() {
    echo -e "\e[31m$1\e[0m"
}

# Check if Python is available
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    print_error "ERROR: Python is not installed or not in PATH"
    print_error "Please install Python 3.8+ and try again"
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo "Using Python: $($PYTHON_CMD --version)"
echo

print_status "[1/5] Installing/updating dependencies..."
$PYTHON_CMD -m pip install --upgrade pip
$PYTHON_CMD -m pip install -r requirements.txt

print_status "[2/5] Cleaning previous build artifacts..."
rm -rf dist/ build/ *.pyc __pycache__/
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

print_status "[3/5] Building executable with PyInstaller..."
$PYTHON_CMD -m PyInstaller --clean nextsight.spec

print_status "[4/5] Verifying build output..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    EXECUTABLE="dist/NextSight-v2.exe"
else
    EXECUTABLE="dist/NextSight-v2"
fi

if [ ! -f "$EXECUTABLE" ]; then
    print_error "ERROR: Executable was not created"
    exit 1
fi

print_status "[5/5] Build completed successfully!"
echo
echo "Executable location: $EXECUTABLE"
echo "File size: $(du -h "$EXECUTABLE" | cut -f1)"

echo
echo "============================================"
echo "Build completed successfully!"
echo "You can find the executable at: $EXECUTABLE"
echo "============================================"

# Make executable runnable on Unix-like systems
if [[ "$OSTYPE" != "msys" && "$OSTYPE" != "win32" ]]; then
    chmod +x "$EXECUTABLE"
    echo "Executable has been made runnable."
fi