@echo off
chcp 65001 > nul

echo Building NHL Card Monitor Auto v13 with enhanced debug logging...

REM Terminate any running instances of the executable to prevent PermissionError
taskkill /f /im "NHL_Card_Monitor_Auto.exe" 2>nul

REM Remove old files
del "dist\NHL_Card_Monitor_Auto.exe" 2>nul
del "build\NHL_Card_Monitor_Auto.exe" 2>nul

REM Build with PyInstaller
pyinstaller --onefile --windowed --name "NHL_Card_Monitor_Auto" nhl_card_monitor_auto.py
set BUILD_RESULT=%errorlevel%

if %BUILD_RESULT% equ 0 (
    echo.
    echo ✅ Build successful! 
    echo 📁 Executable created: dist\NHL_Card_Monitor_Auto.exe
    echo.
    echo 🚀 Features:
    echo   - Fixed player name parsing (no more "Player Stat" or "SPONGE")
    echo   - COMPLETELY FIXED data parsing:
    echo     * Overall: 78 (not "Card Type")
    echo     * Card: "BASE" (not "Card Type")
    echo     * Nationality: "USA" (not "Age")
    echo     * Position: "LW" (not "Shoots")
    echo     * Hand: "LEFT" (not "Shoots")
    echo     * Weight: 89 kg (not "198lb" or "Height")
    echo     * Height: 187 cm (not "6' 2\"" or "Height")
    echo     * Salary: 800000 (not "Division")
    echo   - FIXED image URLs: Real card images instead of logo
    echo   - EUROPEAN units: Weight in kg, height in cm (as numbers)
    echo   - COMPLETE X-Factor abilities detection with proper structure
    echo   - REAL-TIME X-Factor logging in the monitor log
    echo   - FIXED: Backup created BEFORE modifying master.json
    echo   - FIXED: Syntax error in extract_player_stats function
    echo   - Division/League validation - if division is "Division" or empty,
    echo     both division and league fields are removed (not set to NHL)
    echo   - Complete goalie stats parsing:
    echo     * glove_high, stick_high, glove_low, poke_check, stick_low
    echo     * vision, positioning, five_hole, breakaway, shot_recovery, rebound_control
    echo     * card_art field for goalies
    echo   - ENHANCED debug logging for missing URLs detection:
    echo     * Debug logs in find_missing_urls function
    echo     * Shows cards_urls count, master_urls count, found_urls count, missing_urls count
    echo   - Automatic monitoring and updating
    echo.
    echo 📊 Now with enhanced debug logging to fix missing URLs detection!
    echo.
    pause
) else (
    echo.
    echo ❌ Build failed! Error level: %BUILD_RESULT%
    echo Check the error messages above.
    echo.
    pause
)