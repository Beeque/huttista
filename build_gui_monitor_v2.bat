@echo off
chcp 65001 >nul
title NHL Card Monitor - Build GUI v2
echo ========================================
echo    NHL Card Monitor - Build GUI v2
echo ========================================
echo.
echo Building GUI version with IMPROVED name parsing...
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
echo Building IMPROVED GUI executable...
echo.

REM Build the executable
%PYTHON_CMD% -m PyInstaller --onefile --windowed --name "NHL_Card_Monitor_GUI_v2" --add-data "master.json;." nhl_card_monitor_gui_simple.py

if errorlevel 1 (
    echo.
    echo Build failed! Check the error messages above.
    pause
    exit /b 1
)

echo.
echo ✅ Build completed successfully!
echo 📁 Executable location: dist\NHL_Card_Monitor_GUI_v2.exe
echo.
echo 📋 Features included:
echo   • Simple GUI interface (no login required)
echo   • Automatic card monitoring (30 min intervals)
echo   • X-Factor enrichment
echo   • Real-time logging
echo   • Manual card search
echo   • Statistics window
echo   • IMPROVED AUTO-ADD new cards to master.json
echo   • Automatic backup creation
echo   • IMPROVED player name parsing
echo   • Better duplicate detection
echo   • No console window (GUI only)
echo.
echo 🚀 To run the executable:
echo   1. Go to dist\ folder
echo   2. Double-click NHL_Card_Monitor_GUI_v2.exe
echo   3. Start using immediately!
echo.
echo 🔄 Improved Workflow:
echo   1. Click "🔍 Hae uusia kortteja" to find new cards
echo   2. Program fetches detailed card information
echo   3. IMPROVED name parsing for goalies and skaters
echo   4. Shows cards with proper names, OVR, position, team
echo   5. When asked, click "Yes" to add them automatically
echo   6. Cards are added to master.json with backup
echo.
echo 🐛 Bug Fixes v2:
echo   • Fixed: Better player name parsing (no more "NHL HUT Builder")
echo   • Fixed: Improved duplicate detection (by ID and URL)
echo   • Fixed: Better error handling for goalie pages
echo   • Fixed: More accurate card information extraction
echo   • Fixed: Proper display of skipped vs added cards
echo.
pause