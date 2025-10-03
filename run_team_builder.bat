@echo off
chcp 65001 >nul
title NHL Team Builder
echo ========================================
echo    NHL Team Builder - GUI Version
echo ========================================
echo.
echo Starting NHL Team Builder...
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

REM Check if required packages are installed
echo Checking required packages...
%PYTHON_CMD% -c "import requests, PIL" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    %PYTHON_CMD% -m pip install requests Pillow
)

echo.
echo Starting NHL Team Builder GUI...
echo.

REM Run the team builder
%PYTHON_CMD% nhl_team_builder.py

REM Keep window open if there was an error
if errorlevel 1 (
    echo.
    echo Program ended with an error. Press any key to close...
    pause >nul
)