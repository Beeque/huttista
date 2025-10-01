#!/usr/bin/env python3
"""
Build script for NHL Card Browser executable
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def build_executable():
    """Build the executable"""
    print("🏗️  Building NHL Card Browser executable...")
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print("✓ PyInstaller found")
    except ImportError:
        print("✗ PyInstaller not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Clean previous builds
    build_dir = Path("build")
    dist_dir = Path("dist")
    
    if build_dir.exists():
        shutil.rmtree(build_dir)
        print("✓ Cleaned build directory")
    
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
        print("✓ Cleaned dist directory")
    
    # Build command
    cmd = [
        "pyinstaller",
        "--onefile",                    # Single executable file
        "--windowed",                   # No console window
        "--name=NHL_Card_Browser",      # Executable name
        "--add-data=data;data",         # Include data directory
        "--hidden-import=PIL._tkinter_finder",
        "--hidden-import=tkinter",
        "--hidden-import=tkinter.ttk",
        "--hidden-import=requests",
        "--hidden-import=PIL.Image",
        "--hidden-import=PIL.ImageTk",
        "--clean",                      # Clean cache
        "nhl_card_browser.py"
    ]
    
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✓ Build successful!")
        
        # Check if executable was created
        exe_path = Path("dist/NHL_Card_Browser.exe")
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"✓ Executable created: {exe_path}")
            print(f"✓ Size: {size_mb:.1f} MB")
            
            # Copy data directory to dist
            if Path("data").exists():
                shutil.copytree("data", "dist/data", dirs_exist_ok=True)
                print("✓ Data directory copied")
            
            return True
        else:
            print("✗ Executable not found")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"✗ Build failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def create_installer_script():
    """Create a simple installer script"""
    installer_content = '''@echo off
echo NHL Card Browser - Installer
echo ============================

echo Creating directories...
if not exist "C:\\Program Files\\NHL Card Browser" mkdir "C:\\Program Files\\NHL Card Browser"
if not exist "C:\\Program Files\\NHL Card Browser\\data" mkdir "C:\\Program Files\\NHL Card Browser\\data"

echo Copying files...
copy "NHL_Card_Browser.exe" "C:\\Program Files\\NHL Card Browser\\"
xcopy "data\\*" "C:\\Program Files\\NHL Card Browser\\data\\" /E /I

echo Creating desktop shortcut...
echo [InternetShortcut] > "%USERPROFILE%\\Desktop\\NHL Card Browser.url"
echo URL=file:///C:/Program Files/NHL Card Browser/NHL_Card_Browser.exe >> "%USERPROFILE%\\Desktop\\NHL Card Browser.url"
echo IconFile=C:\\Program Files\\NHL Card Browser\\NHL_Card_Browser.exe >> "%USERPROFILE%\\Desktop\\NHL Card Browser.url"
echo IconIndex=0 >> "%USERPROFILE%\\Desktop\\NHL Card Browser.url"

echo Installation complete!
echo You can now run NHL Card Browser from the desktop shortcut.
pause
'''
    
    with open("install.bat", "w") as f:
        f.write(installer_content)
    print("✓ Created install.bat")

def main():
    """Main build process"""
    print("NHL Card Browser - Executable Builder")
    print("=" * 40)
    
    # Check if main script exists
    if not Path("nhl_card_browser.py").exists():
        print("✗ nhl_card_browser.py not found")
        return False
    
    # Check if data directory exists
    if not Path("data").exists():
        print("⚠️  Data directory not found. Creating empty directory...")
        Path("data").mkdir()
    
    # Build executable
    if build_executable():
        print("\n🎉 Build successful!")
        print("Executable location: dist/NHL_Card_Browser.exe")
        
        # Create installer
        create_installer_script()
        
        print("\n📋 Next steps:")
        print("1. Test the executable: dist/NHL_Card_Browser.exe")
        print("2. Copy dist/ folder to target machine")
        print("3. Run install.bat to install")
        
        return True
    else:
        print("\n❌ Build failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)