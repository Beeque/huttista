# 🏒 NHL Team Builder - Installation Guide

## Quick Installation

### Option 1: Automated Setup (Recommended)

**Linux/macOS:**
```bash
git clone <repository-url>
cd <repository-name>
chmod +x build_nhl_team_builder.sh
./build_nhl_team_builder.sh
```

**Windows:**
```cmd
git clone <repository-url>
cd <repository-name>
build_nhl_team_builder.bat
```

### Option 2: Manual Setup

1. **Install Python 3.7+**
   - Download from [python.org](https://www.python.org/downloads/)
   - Make sure to check "Add Python to PATH" during installation

2. **Install tkinter (GUI framework)**
   - **Windows/macOS**: Usually included with Python
   - **Ubuntu/Debian**: `sudo apt-get install python3-tk`
   - **CentOS/RHEL**: `sudo yum install tkinter`

3. **Install dependencies**
   ```bash
   pip install pillow requests
   ```

4. **Download the data file**
   - Ensure `master.json` is in the same directory as `nhl_team_builder.py`

5. **Run the application**
   ```bash
   # Try py first (Windows Python Launcher)
   py nhl_team_builder.py
   
   # OR try python3
   python3 nhl_team_builder.py
   
   # OR try python
   python nhl_team_builder.py
   ```

## Troubleshooting

### Team Dropdown Issues

If the team dropdown only shows "All":

1. **Click the "🔧 Test Dropdowns" button** - This will test the dropdown functionality
2. **Use the test buttons** - Click BOS, TOR, or All to test filtering
3. **Check the debug log** - Look at the bottom of the window for error messages
4. **Refresh the dropdown** - Click the "🔄" button next to the team dropdown
5. **Restart the application** - Close and reopen if issues persist

### Common Issues

**"ModuleNotFoundError: No module named 'tkinter'"**
- Install tkinter: `sudo apt-get install python3-tk` (Linux)
- Or reinstall Python with tkinter support

**"master.json not found"**
- Download the data file from the repository
- Or run the scraper first to generate it

**"No teams showing in dropdown"**
- Check the debug log for error messages
- Try the refresh button (🔄)
- Use the test buttons to verify functionality

## Features

- **76 NHL Teams**: Complete team filtering
- **2,536+ Players**: Full player database
- **Advanced Filtering**: By team, nationality, position, X-Factor
- **Team Building**: Drag and drop interface
- **Budget Management**: Salary cap tracking
- **Debug Tools**: Built-in troubleshooting

## Support

If you encounter issues:
1. Check the debug log at the bottom of the application
2. Try the built-in test buttons
3. Use the refresh functionality
4. Check this troubleshooting guide

## System Requirements

- **Python**: 3.7 or higher
- **OS**: Windows, macOS, or Linux
- **RAM**: 512MB minimum
- **Storage**: 50MB for application + data
- **Network**: Required for card images (optional)