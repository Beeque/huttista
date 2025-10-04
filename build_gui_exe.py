#!/usr/bin/env python3
"""
Build script for creating Windows GUI executable
"""

import subprocess
import sys
import os

def install_pyinstaller():
    """Install PyInstaller if not already installed"""
    try:
        import PyInstaller
        print("PyInstaller already installed")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("PyInstaller installed successfully")

def create_gui_spec_file():
    """Create PyInstaller spec file for GUI version"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['nhl_card_monitor_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('master.json', '.'),
    ],
    hiddenimports=[
        'requests',
        'beautifulsoup4',
        'tkinter',
        'tkinter.ttk',
        'tkinter.scrolledtext',
        'tkinter.messagebox',
        'tkinter.simpledialog',
        'threading',
        'json',
        'time',
        'datetime',
        'logging',
        'urllib.parse',
        'io',
        're',
        'os',
        'sys'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='NHL_Card_Monitor_GUI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    
    with open('nhl_monitor_gui.spec', 'w') as f:
        f.write(spec_content)
    print("Created nhl_monitor_gui.spec file")

def build_gui_executable():
    """Build the GUI executable using PyInstaller"""
    print("Building GUI executable...")
    try:
        subprocess.check_call(['pyinstaller', '--clean', 'nhl_monitor_gui.spec'])
        print("GUI executable built successfully!")
        print("Output: dist/NHL_Card_Monitor_GUI.exe")
    except subprocess.CalledProcessError as e:
        print(f"Error building GUI executable: {e}")
        return False
    return True

def main():
    """Main build function"""
    print("🏒 NHL Card Monitor GUI - Build Script")
    print("=" * 40)
    
    # Install PyInstaller
    install_pyinstaller()
    
    # Create spec file
    create_gui_spec_file()
    
    # Build executable
    if build_gui_executable():
        print("\n✅ GUI Build completed successfully!")
        print("📁 Executable location: dist/NHL_Card_Monitor_GUI.exe")
        print("\n📋 Features included:")
        print("  • Login window with demo mode")
        print("  • Modern GUI interface")
        print("  • Automatic card monitoring (30 min intervals)")
        print("  • X-Factor enrichment")
        print("  • Real-time logging")
        print("  • Manual card search")
        print("  • No console window (GUI only)")
    else:
        print("\n❌ GUI Build failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()