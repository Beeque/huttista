@echo off
echo Building NHL Card Monitor Auto v5 with complete X-Factor enrichment...

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
    echo   - COMPLETE X-Factor abilities detection with proper structure:
    echo     * name: "BIG RIG", "TRUCULENCE", etc.
    echo     * ap_cost: 1, 2, 3, etc.
    echo     * tier: "Specialist", "Elite", etc.
    echo   - FIXED: Backup created BEFORE modifying master.json
    echo   - Automatic monitoring and updating
    echo.
    echo 📊 X-Factor enrichment now includes:
    echo   - Proper ability names from HTML structure
    echo   - AP cost from ability_points div
    echo   - Tier classification from xfactor_category
    echo.
    pause
) else (
    echo.
    echo ❌ Build failed! Check the error messages above.
    echo.
    pause
)