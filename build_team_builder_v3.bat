@echo off
chcp 65001 > nul

echo Building NHL Team Builder v3 with fixed X-Factor dropdown...

REM Terminate any running instances of the executable to prevent PermissionError
taskkill /f /im "NHL_Team_Builder_V2.exe" 2>nul
taskkill /f /im "NHL_Team_Builder.exe" 2>nul

REM Remove old files
del "dist\NHL_Team_Builder_V2.exe" 2>nul
del "dist\NHL_Team_Builder.exe" 2>nul
del "build\NHL_Team_Builder_V2.exe" 2>nul
del "build\NHL_Team_Builder.exe" 2>nul

REM Build with PyInstaller
pyinstaller --onefile --windowed --name "NHL_Team_Builder_V3" nhl_team_builder.py
set BUILD_RESULT=%errorlevel%

if %BUILD_RESULT% equ 0 (
    echo.
    echo ✅ Build successful! 
    echo 📁 Executable created: dist\NHL_Team_Builder_V3.exe
    echo.
    echo 🚀 Features:
    echo   - Fixed X-Factor dropdown TypeError: unhashable type 'dict'
    echo   - Better error handling for X-Factor data processing
    echo   - Handles both string and dictionary X-Factor formats
    echo   - Improved X-Factor name extraction from dictionaries
    echo   - Robust error handling for malformed X-Factor data
    echo   - All previous features maintained:
    echo     * Player card images in slots
    echo     * Nationality, Team, Overall, X-Factor filtering
    echo     * Budget tracking (100M salary cap)
    echo     * Save/Load team lineups
    echo     * Find Cards button integration
    echo     * Real-time log display
    echo     * Goalies section moved to right side
    echo.
    echo 📊 Now with FIXED X-Factor dropdown!
    echo.
    pause
) else (
    echo.
    echo ❌ Build failed! Error level: %BUILD_RESULT%
    echo Check the error messages above.
    echo.
    pause
)