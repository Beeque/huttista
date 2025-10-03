@echo off
chcp 65001 >nul
title Python Test
echo ========================================
echo    Python Test - Find Python Installation
echo ========================================
echo.

echo Testing different Python commands...
echo.

REM Test py launcher
echo 1. Testing 'py' command:
py --version 2>nul
if not errorlevel 1 (
    echo ✅ py command works!
    echo.
    goto :test_pip
) else (
    echo ❌ py command not found
    echo.
)

REM Test python command
echo 2. Testing 'python' command:
python --version 2>nul
if not errorlevel 1 (
    echo ✅ python command works!
    echo.
    goto :test_pip
) else (
    echo ❌ python command not found
    echo.
)

REM Test python3 command
echo 3. Testing 'python3' command:
python3 --version 2>nul
if not errorlevel 1 (
    echo ✅ python3 command works!
    echo.
    goto :test_pip
) else (
    echo ❌ python3 command not found
    echo.
)

echo ❌ No Python installation found!
echo.
echo Please install Python 3.8+ from: https://www.python.org/downloads/
echo Make sure to check "Add Python to PATH" during installation
echo.
pause
exit /b 1

:test_pip
echo Testing pip installation...
echo.

REM Test pip with py
py -m pip --version >nul 2>&1
if not errorlevel 1 (
    echo ✅ pip works with py command
    echo.
    goto :test_packages
)

REM Test pip with python
python -m pip --version >nul 2>&1
if not errorlevel 1 (
    echo ✅ pip works with python command
    echo.
    goto :test_packages
)

echo ❌ pip not found!
echo.
echo Please install pip or reinstall Python
echo.
pause
exit /b 1

:test_packages
echo Testing required packages...
echo.

REM Test requests
py -c "import requests; print('✅ requests installed')" 2>nul
if errorlevel 1 (
    echo ❌ requests not installed
    echo Installing requests...
    py -m pip install requests
)

REM Test beautifulsoup4
py -c "import bs4; print('✅ beautifulsoup4 installed')" 2>nul
if errorlevel 1 (
    echo ❌ beautifulsoup4 not installed
    echo Installing beautifulsoup4...
    py -m pip install beautifulsoup4
)

REM Test tkinter
py -c "import tkinter; print('✅ tkinter installed')" 2>nul
if errorlevel 1 (
    echo ❌ tkinter not installed
    echo tkinter should be included with Python
)

echo.
echo ✅ Python test completed!
echo.
echo You can now run:
echo   - build_exe_py.bat (recommended)
echo   - build_exe_simple_fixed.bat
echo.
pause