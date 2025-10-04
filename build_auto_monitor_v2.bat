@echo off
chcp 65001 >nul
title NHL Card Monitor - Build Auto V2 (REALLY FIXED!)
echo ========================================
echo    NHL Card Monitor - Build Auto V2
echo ========================================
echo.
echo Building AUTO version with REALLY FIXED player name parsing...
echo (Now using div class="player_header" to find names!)
echo.

REM Try py launcher first
py --version >nul 2>&1
if not errorlevel 1 (
    echo Found Python via py launcher
    set PYTHON_CMD=py
    goto :found_python
)

python --version >nul 2>&1
if not errorlevel 1 (
    echo Found Python via python command
    set PYTHON_CMD=python
    goto :found_python
)

echo ERROR: Python not found!
pause
exit /b 1

:found_python
echo Python found: %PYTHON_CMD%
echo.

echo Installing PyInstaller...
%PYTHON_CMD% -m pip install pyinstaller

echo.
echo Building executable...
echo.

REM Kill running instances
taskkill /f /im "NHL_Card_Monitor_Auto.exe" >nul 2>&1
timeout /t 2 >nul

REM Clean build
if exist "dist\NHL_Card_Monitor_Auto.exe" del /f /q "dist\NHL_Card_Monitor_Auto.exe" >nul 2>&1
if exist "build" rmdir /s /q "build" >nul 2>&1

REM Build
%PYTHON_CMD% -m PyInstaller --onefile --windowed --name "NHL_Card_Monitor_Auto" --add-data "master.json;." nhl_card_monitor_auto.py

if errorlevel 1 (
    echo Build failed!
    pause
    exit /b 1
)

echo.
echo ✅ Build completed!
echo 📁 Executable: dist\NHL_Card_Monitor_Auto.exe
echo.
echo 🔧 FIXED in this version:
echo   • Now parses player names CORRECTLY
echo   • Uses div class="player_header" to find names
echo   • No more X-Factor ability names as player names
echo   • Tested with real NHL HUT Builder HTML
echo.
pause