#!/bin/bash

echo "🏒 Building NHL Card Monitor v19 (Linux version)..."
echo ""

# Check if Python is available
echo "🔍 Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found! Please install Python first."
    exit 1
fi
echo "✅ Python found: $(python3 --version)"

# Check if PyInstaller is available
echo "🔍 Checking PyInstaller..."
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "❌ PyInstaller not found! Installing..."
    pip3 install pyinstaller
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install PyInstaller!"
        exit 1
    fi
fi
echo "✅ PyInstaller found"

# Check if main file exists
echo "🔍 Checking main file..."
if [ ! -f "nhl_card_monitor_auto.py" ]; then
    echo "❌ nhl_card_monitor_auto.py not found!"
    exit 1
fi
echo "✅ Main file found"

# Check if requirements are installed
echo "🔍 Checking dependencies..."
if ! python3 -c "import requests, bs4" 2>/dev/null; then
    echo "❌ Missing dependencies! Installing..."
    pip3 install requests beautifulsoup4
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies!"
        exit 1
    fi
fi
echo "✅ Dependencies found"

# Check tkinter
echo "🔍 Checking tkinter..."
if ! python3 -c "import tkinter" 2>/dev/null; then
    echo "⚠️  tkinter missing - GUI will not work"
    echo "   Install with: sudo apt-get install python3-tk"
    echo "   Or run console version instead"
fi

# Clean old files
echo "🗑️ Cleaning old build files..."
rm -rf build/ dist/ *.spec

# Build with PyInstaller
echo "🔨 Building executable..."
pyinstaller --onefile --name "NHL_Card_Monitor_Auto" nhl_card_monitor_auto.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Build successful!"
    echo "📁 Executable: dist/NHL_Card_Monitor_Auto"
    echo ""
    echo "🎯 NEW in v19: Card fetching beyond page 50!"
    echo "   • Removed 10-page limit from all versions"
    echo "   • Now fetches cards from page 50+ automatically"
    echo "   • Smart stopping: only after 50 pages with no missing cards"
    echo "   • Ensures ALL new cards are found and added"
    echo ""
    echo "🏒 NHL Card Monitor v19 ready!"
    echo ""
    echo "🚀 To run: ./dist/NHL_Card_Monitor_Auto"
else
    echo ""
    echo "❌ Build failed!"
    echo "Check the error messages above."
fi