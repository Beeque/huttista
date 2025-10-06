# NHL Team Builder - Installation Guide

## Prerequisites

- Python 3.7 or higher
- Internet connection (for loading player card images)
- `master.json` data file (included in repository)

## Quick Installation

### Option 1: Automated Script (Recommended)

**Linux/macOS:**
```bash
chmod +x build_nhl_team_builder.sh
./build_nhl_team_builder.sh
```

**Windows:**
```cmd
build_nhl_team_builder.bat
```

### Option 2: Manual Installation

1. **Install Python 3:**
   - Download from [python.org](https://www.python.org/downloads/)
   - Make sure to check "Add Python to PATH" during installation

2. **Install tkinter (if not included):**
   - **Ubuntu/Debian:** `sudo apt-get install python3-tk`
   - **macOS:** Usually included with Python
   - **Windows:** Usually included with Python

3. **Install required packages:**
   ```bash
   pip install pillow requests
   ```

4. **Run the application:**
   ```bash
   python3 nhl_team_builder.py
   ```

## Troubleshooting

### Common Issues

**1. "ModuleNotFoundError: No module named 'tkinter'"**
- **Solution:** Install tkinter for your system
- **Ubuntu/Debian:** `sudo apt-get install python3-tk`
- **macOS:** Reinstall Python with tkinter support
- **Windows:** Reinstall Python with tkinter support

**2. "ModuleNotFoundError: No module named 'PIL'"**
- **Solution:** `pip install Pillow`

**3. "ModuleNotFoundError: No module named 'requests'"**
- **Solution:** `pip install requests`

**4. Team dropdown shows only "All"**
- **Solution:** 
  1. Click "🔧 Test Dropdowns" button
  2. Click "🔄" refresh button
  3. Check debug log for errors
  4. Use BOS/TOR/All test buttons

**5. No player images loading**
- **Solution:** Check internet connection and try refreshing

### System Requirements

- **RAM:** 2GB minimum, 4GB recommended
- **Storage:** 100MB for application + data
- **Network:** Internet connection for player images
- **OS:** Windows 10+, macOS 10.14+, or Linux

### Performance Tips

- Close other applications if the GUI is slow
- Use filters to reduce the number of players displayed
- Save your team frequently to avoid losing progress

## Features

- **76 NHL Teams** available for filtering
- **2,536+ Players** with complete stats
- **X-Factor Abilities** filtering
- **Budget Management** with salary tracking
- **Save/Load** team configurations
- **Debug Tools** for troubleshooting

## Support

If you encounter issues:
1. Check the debug log at the bottom of the application
2. Use the built-in test buttons
3. Try refreshing the team dropdown
4. Check that `master.json` is present in the same directory

## Data Source

Player data is sourced from NHL HUT Builder and includes:
- Complete player statistics
- X-Factor abilities
- Team affiliations
- Salary information
- Player images (loaded from web)