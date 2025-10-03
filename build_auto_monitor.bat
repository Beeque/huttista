@echo off
chcp 65001 >nul
title NHL Card Monitor - Build Auto Version
echo ========================================
echo    NHL Card Monitor - Build Auto Version
echo ========================================
echo.
echo Building AUTO version - No buttons, just monitoring...
echo.

REM Try py launcher first (most reliable on Windows)
py --version >nul 2>&1
if not errorlevel 1 (
    echo Found Python via py launcher
    set PYTHON_CMD=py
    goto :found_python
)

REM Fallback to python
python --version >nul 2>&1
if not errorlevel 1 (
    echo Found Python via python command
    set PYTHON_CMD=python
    goto :found_python
)

echo ERROR: Python not found!
echo.
echo Please install Python 3.8+ from: https://www.python.org/downloads/
echo Make sure to check "Add Python to PATH" during installation
echo.
pause
exit /b 1

:found_python
echo Python found: %PYTHON_CMD%
echo.

REM Check if master.json exists
if not exist "master.json" (
    echo WARNING: master.json not found in current directory
    echo Please make sure master.json is in the same folder as this script
    echo.
)

echo Installing PyInstaller...
%PYTHON_CMD% -m pip install pyinstaller

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install PyInstaller
    echo Please check your internet connection and try again
    pause
    exit /b 1
)

echo.
echo Building AUTO GUI executable...
echo.

REM Build the executable
%PYTHON_CMD% -m PyInstaller --onefile --windowed --name "NHL_Card_Monitor_Auto" --add-data "master.json;." nhl_card_monitor_auto.py

if errorlevel 1 (
    echo.
    echo Build failed! Check the error messages above.
    pause
    exit /b 1
)

echo.
echo ✅ Build completed successfully!
echo 📁 Executable location: dist\NHL_Card_Monitor_Auto.exe
echo.
echo 📋 Features included:
echo   • AUTO mode - No buttons, just monitoring
echo   • Automatic card monitoring (30 min intervals)
echo   • Automatic master.json updates
echo   • Real-time logging
echo   • Simple GUI with just log display
echo   • Automatic backup creation
echo   • Improved player name parsing
echo   • Unique ID system for goalies vs skaters
echo   • No console window (GUI only)
echo.
echo 🚀 To run the executable:
echo   1. Go to dist\ folder
echo   2. Double-click NHL_Card_Monitor_Auto.exe
echo   3. Program starts monitoring automatically!
echo.
echo 🔄 Auto Workflow:
echo   1. Program loads master.json automatically
echo   2. Starts monitoring every 30 minutes
echo   3. When new cards found, fetches detailed info
echo   4. Automatically adds new cards to master.json
echo   5. Creates backup before updating
echo   6. Shows all activity in log window
echo   7. Just close window to stop monitoring
echo.
echo 🎯 Perfect for:
echo   • Running in background
echo   • Automatic card database updates
echo   • No user interaction required
echo   • Always up-to-date master.json
echo.
pause