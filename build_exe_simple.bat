@echo off
chcp 65001 >nul
title NHL Card Monitor - Build GUI Executable
echo ========================================
echo    NHL Card Monitor - Build GUI .exe
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo Installing PyInstaller...
pip install pyinstaller

echo.
echo Building GUI executable...
echo.

REM Build the executable
pyinstaller --onefile --windowed --name "NHL_Card_Monitor_GUI" --add-data "master.json;." nhl_card_monitor_gui.py

if errorlevel 1 (
    echo.
    echo Build failed! Check the error messages above.
    pause
    exit /b 1
)

echo.
echo ✅ Build completed successfully!
echo 📁 Executable location: dist\NHL_Card_Monitor_GUI.exe
echo.
echo 📋 Features included:
echo   • Login window with demo mode
echo   • Modern GUI interface  
echo   • Automatic card monitoring (30 min intervals)
echo   • X-Factor enrichment
echo   • Real-time logging
echo   • Manual card search
echo   • No console window (GUI only)
echo.
pause