"""
Build script Windows executable -tiedoston luomiseen.
"""

import sys
import os
import subprocess
from pathlib import Path

def install_pyinstaller():
    """Asentaa PyInstallerin jos se ei ole asennettu."""
    try:
        import PyInstaller
        print("PyInstaller on jo asennettu")
    except ImportError:
        print("Asennetaan PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

def build_executable():
    """Rakentaa Windows executable -tiedoston."""
    print("Rakennetaan Windows executable...")
    
    # PyInstaller-komennot
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=NHL26_HUT_Builder",
        "--icon=icon.ico",  # Jos haluat kuvakkeen
        "--add-data=src;src",  # Sisällytä src-kansio
        "main.py"
    ]
    
    try:
        subprocess.check_call(cmd)
        print("Executable rakennettu onnistuneesti!")
        print("Löydät tiedoston dist/NHL26_HUT_Builder.exe")
    except subprocess.CalledProcessError as e:
        print(f"Virhe executable:n rakentamisessa: {e}")
        return False
    
    return True

def main():
    """Pääfunktio."""
    print("NHL 26 HUT Team Builder - Executable Builder")
    print("=" * 50)
    
    # Tarkista että olemme oikeassa kansiossa
    if not os.path.exists("main.py"):
        print("Virhe: main.py ei löydy. Varmista että olet oikeassa kansiossa.")
        return
    
    # Asenna PyInstaller
    install_pyinstaller()
    
    # Rakenna executable
    if build_executable():
        print("\nRakentaminen valmis!")
        print("Voit jakaa NHL26_HUT_Builder.exe -tiedoston muille käyttäjille.")
    else:
        print("\nRakentaminen epäonnistui.")

if __name__ == "__main__":
    main()