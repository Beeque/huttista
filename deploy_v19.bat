@echo off
echo Deploying NHL Card Monitor v19...
echo.

REM Check if exe exists
if not exist "dist\NHL_Card_Monitor_Auto.exe" (
    echo ❌ Executable not found! Please build first.
    echo Run: build_auto_monitor_v19.bat
    pause
    exit /b 1
)

REM Create deployment directory
if not exist "deploy" mkdir deploy

REM Copy exe
echo 📁 Copying executable...
copy "dist\NHL_Card_Monitor_Auto.exe" "deploy\NHL_Card_Monitor_Auto_v19.exe"

REM Copy master.json if exists
if exist "master.json" (
    echo 📄 Copying master.json...
    copy "master.json" "deploy\master.json"
)

REM Copy README
if exist "BUILD_V19_README.md" (
    echo 📖 Copying README...
    copy "BUILD_V19_README.md" "deploy\README_v19.md"
)

REM Create run script
echo 📝 Creating run script...
echo @echo off > "deploy\RUN_NHL_Monitor_v19.bat"
echo echo Starting NHL Card Monitor v19... >> "deploy\RUN_NHL_Monitor_v19.bat"
echo echo Now with page 50+ support! >> "deploy\RUN_NHL_Monitor_v19.bat"
echo echo. >> "deploy\RUN_NHL_Monitor_v19.bat"
echo NHL_Card_Monitor_Auto_v19.exe >> "deploy\RUN_NHL_Monitor_v19.bat"
echo pause >> "deploy\RUN_NHL_Monitor_v19.bat"

echo.
echo ✅ Deployment complete!
echo.
echo 📁 Files in deploy folder:
dir deploy /b
echo.
echo 🚀 To run: Double-click deploy\RUN_NHL_Monitor_v19.bat
echo.
pause