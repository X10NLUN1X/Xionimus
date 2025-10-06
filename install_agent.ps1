# Xionimus Agent Installer for Windows (PowerShell)
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Xionimus Autonomous Agent - Windows Installation" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "[1/4] Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from https://www.python.org/downloads/" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Install dependencies
Write-Host ""
Write-Host "[2/4] Installing dependencies..." -ForegroundColor Yellow
Set-Location agent
try {
    pip install -r requirements.txt
    Write-Host "Dependencies installed successfully" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Create config file
Write-Host ""
Write-Host "[3/4] Creating configuration file..." -ForegroundColor Yellow
if (!(Test-Path "config.json")) {
    Copy-Item "config.example.json" "config.json"
    Write-Host "Created config.json from template" -ForegroundColor Green
    Write-Host ""
    Write-Host "IMPORTANT: Edit config.json and update:" -ForegroundColor Yellow
    Write-Host "  - backend_url (your Xionimus backend URL)"
    Write-Host "  - watch_directories (your project directories)"
} else {
    Write-Host "config.json already exists" -ForegroundColor Green
}

# Complete
Write-Host ""
Write-Host "[4/4] Installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "1. Edit agent\config.json with your settings"
Write-Host "2. Run: python agent\main.py --config agent\config.json"
Write-Host "3. Configure directories in web UI: http://your-backend/agent"
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter to exit"
