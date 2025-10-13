# NHL Card Monitor v19 Build Script (PowerShell)
# Now with page 50+ support!

Write-Host "🏒 Building NHL Card Monitor v19 (Page 50+ Support)..." -ForegroundColor Green
Write-Host ""

# Kill any running instances
Write-Host "🔄 Terminating running instances..." -ForegroundColor Yellow
Get-Process -Name "NHL_Card_Monitor_Auto" -ErrorAction SilentlyContinue | Stop-Process -Force

# Clean old files
Write-Host "🗑️ Cleaning old build files..." -ForegroundColor Yellow
Remove-Item "dist\NHL_Card_Monitor_Auto.exe" -ErrorAction SilentlyContinue
Remove-Item "build" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "dist" -Recurse -Force -ErrorAction SilentlyContinue

# Build with PyInstaller
Write-Host "🔨 Building executable..." -ForegroundColor Yellow
pyinstaller --onefile --windowed --name "NHL_Card_Monitor_Auto" nhl_card_monitor_auto.py

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Build successful!" -ForegroundColor Green
    Write-Host "📁 Executable: dist\NHL_Card_Monitor_Auto.exe" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "🎯 NEW in v19: Card fetching beyond page 50!" -ForegroundColor Magenta
    Write-Host "   • Removed 10-page limit from all versions" -ForegroundColor White
    Write-Host "   • Now fetches cards from page 50+ automatically" -ForegroundColor White
    Write-Host "   • Smart stopping: only after 50 pages with no missing cards" -ForegroundColor White
    Write-Host "   • Ensures ALL new cards are found and added" -ForegroundColor White
    Write-Host ""
    Write-Host "🏒 NHL Card Monitor v19 ready!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "❌ Build failed! Error code: $LASTEXITCODE" -ForegroundColor Red
    Write-Host "Check the error messages above." -ForegroundColor Red
}

Write-Host ""
Read-Host "Press Enter to continue"