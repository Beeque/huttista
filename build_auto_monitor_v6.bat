@echo off
echo Building NHL Card Monitor Auto v6 with real-time X-Factor logging...

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
    echo   - COMPLETE X-Factor abilities detection with proper structure
    echo   - REAL-TIME X-Factor logging in the monitor log
    echo   - FIXED: Backup created BEFORE modifying master.json
    echo   - Automatic monitoring and updating
    echo.
    echo 📊 Now you'll see in the log:
    echo   [10:10:15] Haettu: CLAYTON KELLER
    echo   [10:10:15] X-Factor kyvyt: WHEELS, QUICK DRAW
    echo   [10:10:16] Haettu: MATVEI MICHKOV
    echo   [10:10:16] Ei X-Factor kykyjä
    echo.
    pause
) else (
    echo.
    echo ❌ Build failed! Check the error messages above.
    echo.
    pause
)