@echo off
REM NHL Team Builder - Build and Run Script for Windows
REM This script sets up and runs the NHL Team Builder application

echo 🏒 NHL Team Builder - Build and Run Script
echo ==========================================

REM Check if Python is installed
py --version >nul 2>&1
if errorlevel 1 (
    python --version >nul 2>&1
    if errorlevel 1 (
        echo ❌ Python is not installed. Please install Python first.
        echo    Download from: https://www.python.org/downloads/
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=python
        echo ✅ Python found
        python --version
    )
) else (
    set PYTHON_CMD=py
    echo ✅ Python found
    py --version
)

REM Check if master.json exists
if not exist "master.json" (
    echo ❌ master.json not found. Please ensure the data file is present.
    echo    You can download it from the repository or run the scraper first.
    pause
    exit /b 1
)

echo ✅ master.json found

REM Create virtual environment (optional but recommended)
if not exist "venv" (
    echo 🔧 Creating virtual environment...
    %PYTHON_CMD% -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
if exist "requirements.txt" (
    echo 📦 Installing requirements...
    pip install -r requirements.txt
)

REM Install additional packages if needed
echo 📦 Installing additional packages...
pip install pillow requests

echo.
echo 🚀 Starting NHL Team Builder...
echo ================================
echo.
echo Instructions:
echo 1. Use the Team dropdown to filter players by NHL team
echo 2. Use the test buttons (BOS, TOR, All) to test filtering
echo 3. Click 'Test Dropdowns' to debug any issues
echo 4. Check the debug log at the bottom for troubleshooting
echo.

REM Run the application
%PYTHON_CMD% nhl_team_builder.py

echo.
echo 👋 NHL Team Builder closed. Thanks for using it!
pause