@echo off
echo Testing NHL Card Monitor v19 build process...
echo.

REM Check if Python is available
echo 🔍 Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found! Please install Python first.
    pause
    exit /b 1
)
echo ✅ Python found

REM Check if PyInstaller is available
echo 🔍 Checking PyInstaller...
python -c "import PyInstaller" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ PyInstaller not found! Installing...
    pip install pyinstaller
    if %errorlevel% neq 0 (
        echo ❌ Failed to install PyInstaller!
        pause
        exit /b 1
    )
)
echo ✅ PyInstaller found

REM Check if main file exists
echo 🔍 Checking main file...
if not exist "nhl_card_monitor_auto.py" (
    echo ❌ nhl_card_monitor_auto.py not found!
    pause
    exit /b 1
)
echo ✅ Main file found

REM Check if requirements are installed
echo 🔍 Checking dependencies...
python -c "import requests, bs4, tkinter" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Missing dependencies! Installing...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ❌ Failed to install dependencies!
        pause
        exit /b 1
    )
)
echo ✅ Dependencies found

echo.
echo ✅ All checks passed! Ready to build.
echo.
echo 🚀 Run one of these to build:
echo   - build_auto_monitor_v19.bat (full build)
echo   - build_v19_simple.bat (simple build)
echo   - build_v19.ps1 (PowerShell)
echo.
pause