@echo off
REM Build script for NextSight v2 Windows executable
REM This script builds a standalone .exe file using PyInstaller

echo ============================================
echo NextSight v2 - Build Script (Windows)
echo ============================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo [1/5] Installing/updating dependencies...
pip install --upgrade pip
pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [2/5] Cleaning previous build artifacts...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

echo.
echo [3/5] Building executable with PyInstaller...
pyinstaller --clean nextsight.spec

if errorlevel 1 (
    echo ERROR: PyInstaller build failed
    pause
    exit /b 1
)

echo.
echo [4/5] Verifying build output...
if not exist "dist\NextSight-v2.exe" (
    echo ERROR: Executable was not created
    pause
    exit /b 1
)

echo.
echo [5/5] Build completed successfully!
echo.
echo Executable location: dist\NextSight-v2.exe
echo File size: 
for %%A in ("dist\NextSight-v2.exe") do echo %%~zA bytes

echo.
echo ============================================
echo Build completed successfully!
echo You can find the executable at: dist\NextSight-v2.exe
echo ============================================
pause