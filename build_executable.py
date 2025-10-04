#!/usr/bin/env python3
"""
Build script for creating Windows executable
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

def create_spec_file():
    """Create PyInstaller spec file"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['nhl_card_monitor_enhanced.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('update_missing_cards_final.py', '.'),
        ('enrich_country_xfactors.py', '.'),
        ('utils_clean.py', '.'),
    ],
    hiddenimports=[
        'requests',
        'beautifulsoup4',
        'PIL',
        'tkinter',
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
    name='NHL_Card_Monitor',
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
    icon='nhl_icon.ico' if os.path.exists('nhl_icon.ico') else None,
)
'''
    
    with open('nhl_monitor.spec', 'w') as f:
        f.write(spec_content)
    print("Created nhl_monitor.spec file")

def build_executable():
    """Build the executable using PyInstaller"""
    print("Building executable...")
    try:
        subprocess.check_call(['pyinstaller', '--clean', 'nhl_monitor.spec'])
        print("Executable built successfully!")
        print("Output: dist/NHL_Card_Monitor.exe")
    except subprocess.CalledProcessError as e:
        print(f"Error building executable: {e}")
        return False
    return True

def main():
    """Main build function"""
    print("🏒 NHL Card Monitor - Build Script")
    print("=" * 40)
    
    # Install PyInstaller
    install_pyinstaller()
    
    # Create spec file
    create_spec_file()
    
    # Build executable
    if build_executable():
        print("\n✅ Build completed successfully!")
        print("📁 Executable location: dist/NHL_Card_Monitor.exe")
        print("\n📋 Features included:")
        print("  • Automatic card monitoring (30 min intervals)")
        print("  • X-Factor enrichment")
        print("  • Card image display")
        print("  • Real-time logging")
        print("  • Manual card search")
    else:
        print("\n❌ Build failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()