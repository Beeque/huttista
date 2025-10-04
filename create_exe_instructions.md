# 🏒 NHL Card Monitor - .exe Tiedoston Luonti

## 📋 Vaatimukset Windows-koneella

### 1. Python 3.8+ asennettuna
```cmd
python --version
```

### 2. Asenna PyInstaller
```cmd
pip install pyinstaller
```

### 3. Asenna muut riippuvuudet
```cmd
pip install requests beautifulsoup4 Pillow
```

## 🚀 .exe Tiedoston Luonti

### Vaihe 1: Lataa tiedostot
Lataa kaikki tiedostot samaan kansioon:
- `nhl_card_monitor_console.py`
- `update_missing_cards_final.py`
- `enrich_country_xfactors.py`
- `utils_clean.py`
- `master.json`

### Vaihe 2: Luo PyInstaller spec-tiedosto
Luo tiedosto `nhl_monitor.spec`:

```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['nhl_card_monitor_console.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('update_missing_cards_final.py', '.'),
        ('enrich_country_xfactors.py', '.'),
        ('utils_clean.py', '.'),
        ('master.json', '.'),
    ],
    hiddenimports=[
        'requests',
        'beautifulsoup4',
        'PIL',
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
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
```

### Vaihe 3: Rakenna .exe
```cmd
pyinstaller --clean nhl_monitor.spec
```

### Vaihe 4: Tarkista tulos
- **Sijainti**: `dist/NHL_Card_Monitor.exe`
- **Koko**: ~50-100 MB
- **Testaa**: Kaksoisklikkaa .exe tiedostoa

## 🎯 Yksinkertaisempi tapa

### Automaattinen build-skripti
Luo tiedosto `build_exe.bat`:

```batch
@echo off
echo Building NHL Card Monitor executable...
echo.

REM Install PyInstaller if not installed
pip install pyinstaller

REM Build the executable
pyinstaller --onefile --console --name "NHL_Card_Monitor" --add-data "update_missing_cards_final.py;." --add-data "enrich_country_xfactors.py;." --add-data "utils_clean.py;." --add-data "master.json;." nhl_card_monitor_console.py

echo.
echo Build complete! Check dist/NHL_Card_Monitor.exe
pause
```

### Aja build-skripti
```cmd
build_exe.bat
```

## 🔧 Vianmääritys

### Virhe: "No module named 'requests'"
```cmd
pip install requests beautifulsoup4
```

### Virhe: "PyInstaller not found"
```cmd
pip install pyinstaller
```

### Virhe: "master.json not found"
- Varmista että `master.json` on samassa kansiossa
- Tarkista tiedoston nimi (case-sensitive)

### Suuri .exe koko
- Normaali koko: 50-100 MB
- Sisältää Python-runtime ja kaikki riippuvuudet
- Ei vaadi Python-asennusta kohdekoneella

## 📦 Jakelu

### Tarvittavat tiedostot
- `NHL_Card_Monitor.exe` - Pääohjelma
- `master.json` - Pelaajien tietokanta (vaihtoehtoinen)

### Asennusohje
1. Lataa `NHL_Card_Monitor.exe`
2. Aseta haluamaasi kansioon
3. Kaksoisklikkaa käynnistääksesi
4. Lataa `master.json` samaan kansioon (jos ei toimi)

## 🚀 GitHub Release

### Luo GitHub Release
1. **Tag**: `v1.0.0`
2. **Title**: `NHL Card Monitor v1.0.0`
3. **Description**: 
   ```
   🏒 NHL Card Monitor - Windows Executable
   
   Automaattinen korttien seuranta NHL HUT Builderille
   
   Ominaisuudet:
   - Automaattinen seuranta (30 min välein)
   - X-Factor rikastus
   - Korttien kuvat
   - Reaaliaikainen loggaus
   ```

### Lataa tiedostot
- `NHL_Card_Monitor.exe` (Assets)
- `master.json` (Assets)
- `INSTALL_WINDOWS.md` (Assets)

### Release Notes
```
## 🆕 Uudet ominaisuudet
- Automaattinen korttien seuranta
- X-Factor kykyjen rikastus
- Korttien kuvien näyttö
- Reaaliaikainen loggaus

## 🔧 Tekniset parannukset
- Robusti virheenkäsittely
- Automaattiset uudelleenyritykset
- Threading ei-jäädyttävään käyttöliittymään

## 📋 Vaatimukset
- Windows 10/11
- Internet-yhteys
- Ei Python-asennusta tarvita
```

---

**🏒 NHL Card Monitor** - Valmis Windows executable:ksi!