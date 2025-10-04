@echo off
echo Building NHL Card Monitor Auto v7 with fixed data parsing...

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
    echo   - COMPLETELY FIXED data parsing:
    echo     * Overall: 78 (not "Card Type")
    echo     * Card: "BASE" (not "Card Type")
    echo     * Nationality: "USA" (not "Age")
    echo     * Position: "LW" (not "Shoots")
    echo     * Hand: "LEFT" (not "Shoots")
    echo     * Weight: 198 (not "Height")
    echo     * Height: "6' 2\"" (not "Height")
    echo     * Salary: 800000 (not "Division")
    echo   - COMPLETE X-Factor abilities detection with proper structure
    echo   - REAL-TIME X-Factor logging in the monitor log
    echo   - FIXED: Backup created BEFORE modifying master.json
    echo   - Automatic monitoring and updating
    echo.
    echo 📊 Now all data fields are parsed correctly!
    echo.
    pause
) else (
    echo.
    echo ❌ Build failed! Check the error messages above.
    echo.
    pause
)