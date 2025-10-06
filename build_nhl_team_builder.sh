#!/bin/bash

# NHL Team Builder - Build and Run Script
# This script sets up and runs the NHL Team Builder application

echo "🏒 NHL Team Builder - Build and Run Script"
echo "=========================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if required packages are installed
echo "📦 Checking required packages..."

# Function to check and install package
check_package() {
    local package=$1
    if python3 -c "import $package" 2>/dev/null; then
        echo "✅ $package is installed"
    else
        echo "❌ $package is not installed. Installing..."
        pip3 install $package
    fi
}

# Check and install required packages
check_package "tkinter" || {
    echo "⚠️  tkinter might not be available. On Ubuntu/Debian, install with:"
    echo "   sudo apt-get install python3-tk"
    echo "   On macOS: tkinter should be included with Python"
    echo "   On Windows: tkinter should be included with Python"
}

# Check if master.json exists
if [ ! -f "master.json" ]; then
    echo "❌ master.json not found. Please ensure the data file is present."
    echo "   You can download it from the repository or run the scraper first."
    exit 1
fi

echo "✅ master.json found"

# Create virtual environment (optional but recommended)
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install requirements
if [ -f "requirements.txt" ]; then
    echo "📦 Installing requirements..."
    pip install -r requirements.txt
fi

# Install additional packages if needed
echo "📦 Installing additional packages..."
pip install pillow requests

echo ""
echo "🚀 Starting NHL Team Builder..."
echo "================================"
echo ""
echo "Instructions:"
echo "1. Use the Team dropdown to filter players by NHL team"
echo "2. Use the test buttons (BOS, TOR, All) to test filtering"
echo "3. Click 'Test Dropdowns' to debug any issues"
echo "4. Check the debug log at the bottom for troubleshooting"
echo ""

# Run the application
python3 nhl_team_builder.py

echo ""
echo "👋 NHL Team Builder closed. Thanks for using it!"