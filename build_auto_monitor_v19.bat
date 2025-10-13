@echo off
chcp 65001 > nul

echo Building NHL Card Monitor Auto v19 with page 50+ improvements...
echo.

REM Terminate any running instances of the executable to prevent PermissionError
echo 🔄 Terminating any running instances...
taskkill /f /im "NHL_Card_Monitor_Auto.exe" 2>nul

REM Remove old files
echo 🗑️ Cleaning old build files...
del "dist\NHL_Card_Monitor_Auto.exe" 2>nul
del "build\NHL_Card_Monitor_Auto.exe" 2>nul
rmdir /s /q "build" 2>nul
rmdir /s /q "dist" 2>nul

echo.
echo 🔨 Building with PyInstaller...
pyinstaller --onefile --windowed --name "NHL_Card_Monitor_Auto" nhl_card_monitor_auto.py
set BUILD_RESULT=%errorlevel%

if %BUILD_RESULT% equ 0 (
    echo.
    echo ✅ Build successful! 
    echo 📁 Executable created: dist\NHL_Card_Monitor_Auto.exe
    echo.
    echo 🚀 NEW FEATURES in v19:
    echo   🎯 MAJOR IMPROVEMENT: Card fetching beyond page 50!
    echo     * Removed 10-page limit from ALL versions
    echo     * Now fetches cards from page 50+ automatically
    echo     * Smart 50-page check: stops only if no missing cards found
    echo     * Continues searching even if individual pages have no missing cards
    echo     * This ensures ALL new cards are found and added to database
    echo.
    echo   📋 Fixed files (11 total):
    echo     * nhl_card_monitor_auto.py (already fixed)
    echo     * nhl_card_monitor_console.py
    echo     * nhl_card_monitor_console_fixed.py
    echo     * nhl_card_monitor_console_windows.py
    echo     * nhl_card_monitor_gui.py
    echo     * nhl_card_monitor_gui_simple.py
    echo     * nhl_card_monitor_enhanced.py
    echo     * nhl_card_monitor_standalone.py
    echo     * nhl_card_monitor.py
    echo     * update_missing_cards_final.py
    echo     * update_missing_cards_final_windows.py
    echo.
    echo   🔧 Technical improvements:
    echo     * while True loop instead of page <= max_pages
    echo     * Intelligent stopping: only after 50 pages with no missing cards
    echo     * Preserves performance with smart limits
    echo     * All versions now consistent with page 50+ support
    echo.
    echo   🎮 Previous features still included:
    echo     * Fixed player name parsing
    echo     * Complete data parsing (Overall, Card, Nationality, etc.)
    echo     * European units (kg, cm)
    echo     * X-Factor abilities detection
    echo     * Performance optimizations
    echo     * Concurrent fetching
    echo     * Automatic monitoring
    echo.
    echo 🏒 NHL Card Monitor v19 - Now fetches ALL cards beyond page 50!
    echo.
    echo 📝 To run: Double-click dist\NHL_Card_Monitor_Auto.exe
    echo.
    pause
) else (
    echo.
    echo ❌ Build failed! Error level: %BUILD_RESULT%
    echo Check the error messages above.
    echo.
    echo 💡 Common solutions:
    echo   - Make sure Python and PyInstaller are installed
    echo   - Run as Administrator if permission issues
    echo   - Check that nhl_card_monitor_auto.py exists
    echo.
    pause
)