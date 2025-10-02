#!/usr/bin/env python3
"""
Build script for creating Windows executables from cards_monitor.py
Creates both windowed and console versions
"""

import subprocess
import sys
import os

def install_pyinstaller():
    """Install PyInstaller if not already installed"""
    try:
        import PyInstaller
        print("✅ PyInstaller already installed")
    except ImportError:
        print("📦 Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller installed successfully")

def build_windowed_executable():
    """Build the windowed (background service) executable"""
    print("🔨 Building windowed executable (background service)...")
    
    cmd = [
        "pyinstaller",
        "--onefile",  # Single executable file
        "--windowed",  # No console window
        "--name", "NHL_Cards_Monitor_Service",
        "--add-data", "utils_clean.py;.",  # Include utils_clean.py
        "--add-data", "master.json;.",  # Include master.json if exists
        "--hidden-import", "requests",
        "--hidden-import", "beautifulsoup4",
        "--hidden-import", "bs4",
        "cards_monitor.py"
    ]
    
    try:
        subprocess.check_call(cmd)
        print("✅ Windowed executable built successfully!")
        print("📁 Output: dist/NHL_Cards_Monitor_Service.exe")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error building windowed executable: {e}")
        return False
    
    return True

def build_console_executable():
    """Build the console executable"""
    print("🔨 Building console executable...")
    
    cmd = [
        "pyinstaller",
        "--onefile",  # Single executable file
        "--console",  # Keep console window
        "--name", "NHL_Cards_Monitor_Console",
        "--add-data", "utils_clean.py;.",  # Include utils_clean.py
        "--add-data", "master.json;.",  # Include master.json if exists
        "--hidden-import", "requests",
        "--hidden-import", "beautifulsoup4",
        "--hidden-import", "bs4",
        "cards_monitor_console.py"
    ]
    
    try:
        subprocess.check_call(cmd)
        print("✅ Console executable built successfully!")
        print("📁 Output: dist/NHL_Cards_Monitor_Console.exe")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error building console executable: {e}")
        return False
    
    return True

def create_readme():
    """Create comprehensive README for the executables"""
    readme_content = """# NHL HUT Builder Cards Monitor - Windows Executables

## Overview
This package contains Windows executables that automatically monitor the NHL HUT Builder cards page for new cards and add them to master.json.

## Files Included
- `NHL_Cards_Monitor_Service.exe` - Background service (no console window)
- `NHL_Cards_Monitor_Console.exe` - Console version (shows activity)
- `utils_clean.py` - Data cleaning utilities (required)
- `master.json` - Your existing database (if available)

## Features
- 🔍 Monitors default view every 30 minutes
- 🆕 Automatically detects new cards
- 📊 Adds X-Factor abilities to new cards
- 💾 Creates automatic backups before changes
- 📝 Detailed logging of all activities
- 🌍 Follows EU data standards (cm, kg, etc.)
- 🔄 Maintains data consistency with existing scrapers
- 🛡️ Error handling and recovery

## Usage Options

### Option 1: Background Service (Recommended)
1. Run `NHL_Cards_Monitor_Service.exe`
2. The monitor runs silently in the background
3. Check `cards_monitor.log` for activity details
4. Stop by ending the process in Task Manager

### Option 2: Console Version (For Debugging)
1. Run `NHL_Cards_Monitor_Console.exe`
2. See real-time activity in the console window
3. Press Ctrl+C to stop the monitor

## Setup Instructions
1. Create a new folder for the monitor
2. Copy all files to this folder:
   - `NHL_Cards_Monitor_Service.exe` (or Console version)
   - `utils_clean.py` (required)
   - `master.json` (your existing database)
3. Run the executable
4. The monitor will create additional files as needed

## Files Created by Monitor
- `cards_monitor.log` - Detailed activity log
- `backups/` - Automatic backups of master.json
- Updated `master.json` - With new cards added

## Configuration
- **Monitoring interval**: 30 minutes
- **Cards checked per cycle**: 100 (most recent)
- **Automatic X-Factor data fetching**: Yes
- **EU unit conversion**: Height in cm, weight in kg
- **Data cleaning**: HTML stripping, numeric conversion

## Logging
All activities are logged to `cards_monitor.log` including:
- Monitoring cycle start/end times
- New card detection
- X-Factor data fetching progress
- Database update operations
- Error handling and recovery
- Backup creation

## Data Standards
The monitor follows the same data standards as existing scrapers:
- **Height**: Converted to centimeters (cm)
- **Weight**: Converted to kilograms (kg)
- **Salary**: Numeric format (e.g., 5000000 for $5M)
- **Stats**: All numeric values properly formatted
- **HTML**: Stripped from all text fields
- **X-Factors**: Complete with tier information (Specialist/All-Star/Elite)

## Requirements
- Windows 10/11
- Internet connection
- Write permissions in the executable directory
- `utils_clean.py` in the same directory
- `master.json` in the same directory (will be created if missing)

## Troubleshooting
1. **Check `cards_monitor.log`** for detailed error information
2. **Verify internet connection** - monitor needs to access NHL HUT Builder
3. **Check file permissions** - monitor needs to write files
4. **Ensure required files** are in the same directory as the executable
5. **Check antivirus software** - may block the executable

## Support
- Check `cards_monitor.log` for detailed information about any issues
- Monitor creates automatic backups in `backups/` folder
- Console version shows real-time activity for debugging

## Security
- Monitor only reads from NHL HUT Builder API
- All data is processed locally
- Automatic backups prevent data loss
- No personal data is collected or transmitted
"""
    
    with open("README_Monitor_Executables.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("📝 Created README_Monitor_Executables.txt")

def copy_required_files():
    """Copy required files to dist directory"""
    print("📁 Copying required files to dist directory...")
    
    dist_dir = "dist"
    if not os.path.exists(dist_dir):
        os.makedirs(dist_dir)
    
    files_to_copy = [
        "utils_clean.py",
        "master.json"  # Only if it exists
    ]
    
    for file in files_to_copy:
        if os.path.exists(file):
            try:
                import shutil
                shutil.copy2(file, dist_dir)
                print(f"✅ Copied {file} to dist/")
            except Exception as e:
                print(f"⚠️ Could not copy {file}: {e}")
        else:
            print(f"ℹ️ {file} not found (optional)")

def main():
    print("🏒 NHL HUT Builder Cards Monitor - Build Script")
    print("=" * 60)
    
    # Install PyInstaller
    install_pyinstaller()
    
    # Build executables
    windowed_success = build_windowed_executable()
    console_success = build_console_executable()
    
    if windowed_success and console_success:
        # Copy required files
        copy_required_files()
        
        # Create README
        create_readme()
        
        print("\n✅ Build completed successfully!")
        print("📁 Files created in dist/ directory:")
        print("  - NHL_Cards_Monitor_Service.exe (Background service)")
        print("  - NHL_Cards_Monitor_Console.exe (Console version)")
        print("  - utils_clean.py (Required)")
        print("  - master.json (If available)")
        print("  - README_Monitor_Executables.txt (Instructions)")
        
        print("\n💡 Usage:")
        print("  1. Copy entire dist/ folder to desired location")
        print("  2. Run NHL_Cards_Monitor_Service.exe for background monitoring")
        print("  3. Or run NHL_Cards_Monitor_Console.exe for console output")
        print("  4. Monitor will automatically start checking every 30 minutes")
        
    else:
        print("❌ Build failed!")

if __name__ == '__main__':
    main()