# NHL Card Monitor - PowerShell Launcher
# Windows 11 compatible

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   NHL Card Monitor - Console Version" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>$null
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ and try again" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if master.json exists
if (Test-Path "master.json") {
    Write-Host "✅ master.json found" -ForegroundColor Green
} else {
    Write-Host "⚠️  WARNING: master.json not found in current directory" -ForegroundColor Yellow
    Write-Host "Please make sure master.json is in the same folder as this script" -ForegroundColor Yellow
    Write-Host ""
}

# Check if the monitor script exists
if (Test-Path "nhl_card_monitor_console.py") {
    Write-Host "✅ NHL Card Monitor script found" -ForegroundColor Green
} else {
    Write-Host "❌ ERROR: nhl_card_monitor_console.py not found" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "🚀 Starting NHL Card Monitor..." -ForegroundColor Green
Write-Host ""

# Run the monitor
try {
    python nhl_card_monitor_console.py
} catch {
    Write-Host ""
    Write-Host "❌ Program ended with an error" -ForegroundColor Red
    Read-Host "Press Enter to close"
}