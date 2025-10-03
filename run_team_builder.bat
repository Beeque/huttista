@echo off
chcp 65001 >nul
title NHL Team Builder - Run
echo ========================================
echo    NHL Team Builder - Run
echo ========================================
echo.
echo Starting NHL Team Builder...
echo.

REM Try py launcher first
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
    echo ERROR: master.json not found!
    echo Please make sure master.json is in the same folder as this script
    echo.
    pause
    exit /b 1
)

echo Installing required packages...
%PYTHON_CMD% -m pip install pillow requests beautifulsoup4

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install required packages
    echo Please check your internet connection and try again
    pause
    exit /b 1
)

echo.
echo Starting NHL Team Builder...
echo.

REM Run the team builder
%PYTHON_CMD% nhl_team_builder.py

echo.
echo NHL Team Builder closed.
pause