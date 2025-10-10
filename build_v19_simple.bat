@echo off
echo Building NHL Card Monitor v19 (Page 50+ Support)...
echo.

REM Kill running instances
taskkill /f /im "NHL_Card_Monitor_Auto.exe" 2>nul

REM Clean and build
del "dist\NHL_Card_Monitor_Auto.exe" 2>nul
pyinstaller --onefile --windowed --name "NHL_Card_Monitor_Auto" nhl_card_monitor_auto.py

if %errorlevel% equ 0 (
    echo.
    echo ✅ Build complete! 
    echo 📁 File: dist\NHL_Card_Monitor_Auto.exe
    echo 🎯 Now supports fetching cards beyond page 50!
    echo.
) else (
    echo ❌ Build failed!
)

pause