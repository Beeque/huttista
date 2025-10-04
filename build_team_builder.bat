@echo off
chcp 65001 >nul
title NHL Team Builder - Build Executable
echo ========================================
echo    NHL Team Builder - Build Executable
echo ========================================
echo.
echo Building NHL Team Builder executable...
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

echo Installing required packages...
%PYTHON_CMD% -m pip install pyinstaller pillow requests beautifulsoup4

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install required packages
    echo Please check your internet connection and try again
    pause
    exit /b 1
)

echo.
echo Building NHL Team Builder executable...
echo.

REM Kill any running instances first
echo Checking for running instances...
taskkill /f /im "NHL_Team_Builder.exe" >nul 2>&1
timeout /t 2 >nul

REM Clean previous build
if exist "dist\NHL_Team_Builder.exe" (
    echo Removing old executable...
    del /f /q "dist\NHL_Team_Builder.exe" >nul 2>&1
)

if exist "build" (
    echo Cleaning build directory...
    rmdir /s /q "build" >nul 2>&1
)

REM Build the executable
%PYTHON_CMD% -m PyInstaller --onefile --windowed --name "NHL_Team_Builder" --add-data "master.json;." nhl_team_builder.py

if errorlevel 1 (
    echo.
    echo Build failed! Check the error messages above.
    pause
    exit /b 1
)

echo.
echo ✅ Build completed successfully!
echo 📁 Executable location: dist\NHL_Team_Builder.exe
echo.
echo 📋 Features included:
echo   • Team lineup builder with 4 forward lines
echo   • 3 defensive pairs + 1 goalie pair
echo   • Player filtering by nationality, team, overall
echo   • Search functionality
echo   • Budget tracking (100M salary cap)
echo   • Save/Load team lineups
echo   • Drag & drop player assignment
echo   • Real-time budget calculations
echo   • Card image display (when available)
echo   • Flexible position assignments
echo.
echo 🚀 To run the executable:
echo   1. Go to dist\ folder
echo   2. Double-click NHL_Team_Builder.exe
echo   3. Start building your team!
echo.
echo 🏒 Team Builder Features:
echo   • 4 Forward Lines (LW-C-RW)
echo   • 3 Defense Pairs (LD-RD)
echo   • 2 Goalies (Starter + Backup)
echo   • Filter by nationality, team, overall rating
echo   • Search players by name
echo   • Budget tracking with salary cap
echo   • Save/load team configurations
echo   • Flexible position assignments
echo   • Card image display
echo.
echo 🎯 Perfect for:
echo   • Building optimal lineups
echo   • Testing different combinations
echo   • Budget management
echo   • Team strategy planning
echo   • Chemistry optimization (future)
echo.
pause