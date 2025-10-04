@echo off
echo Building NHL Card Monitor Auto v4 with fixed backup logic...

REM Kill any running instances
taskkill /f /im "NHL_Card_Monitor_Auto.exe" 2>nul

REM Remove old files
del "dist\NHL_Card_Monitor_Auto.exe" 2>nul
del "build\NHL_Card_Monitor_Auto.exe" 2>nul

REM Build with PyInstaller
pyinstaller --onefile --windowed --name "NHL_Card_Monitor_Auto" nhl_card_monitor_auto.py

if %errorlevel% equ 0 (
    echo.
    echo ✅ Build successful! 
    echo 📁 Executable created: dist\NHL_Card_Monitor_Auto.exe
    echo.
    echo 🚀 Features:
    echo   - Fixed player name parsing (no more "Player Stat" or "SPONGE")
    echo   - Complete stats extraction (overall, nationality, position, etc.)
    echo   - X-Factor abilities detection
    echo   - FIXED: Backup created BEFORE modifying master.json (not after!)
    echo   - Automatic monitoring and updating
    echo.
    pause
) else (
    echo.
    echo ❌ Build failed! Check the error messages above.
    echo.
    pause
)