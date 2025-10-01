@echo off
echo NHL Card Browser - Executable Builder
echo ====================================

echo Installing PyInstaller...
pip install pyinstaller

echo.
echo Building executable...
pyinstaller --onefile --windowed --name=NHL_Card_Browser --add-data="data;data" --hidden-import=PIL._tkinter_finder --hidden-import=tkinter --hidden-import=tkinter.ttk --hidden-import=requests --hidden-import=PIL.Image --hidden-import=PIL.ImageTk --clean nhl_card_browser.py

echo.
echo Copying data directory...
if exist "data" xcopy "data" "dist\data" /E /I

echo.
echo Build complete!
echo Executable: dist\NHL_Card_Browser.exe
echo.
pause