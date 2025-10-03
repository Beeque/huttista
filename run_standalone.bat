@echo off
chcp 65001 >nul
title NHL Card Monitor - Standalone
echo ========================================
echo    NHL Card Monitor - Standalone
echo ========================================
echo.
echo Starting NHL Card Monitor...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if master.json exists
if not exist "master.json" (
    echo WARNING: master.json not found in current directory
    echo Please make sure master.json is in the same folder as this script
    echo.
)

REM Run the standalone monitor
python nhl_card_monitor_standalone.py

REM Keep window open if there was an error
if errorlevel 1 (
    echo.
    echo Program ended with an error. Press any key to close...
    pause >nul
)