# ─────────────────────────────────────────────────────────────────────────────
# IoT Automatic Door System — Backend Setup Script (Windows PowerShell)
# Usage: .\scripts\setup.ps1
# ─────────────────────────────────────────────────────────────────────────────

$ErrorActionPreference = "Stop"

function Log  { Write-Host "[SETUP] $args" -ForegroundColor Cyan }
function Ok   { Write-Host "[OK]    $args" -ForegroundColor Green }
function Warn { Write-Host "[WARN]  $args" -ForegroundColor Yellow }

Log "IoT Automatic Door System — Backend Setup (Windows)"
Write-Host "────────────────────────────────────────────"

# 1. Python version
Log "Checking Python version..."
$pyver = python --version 2>&1
if ($pyver -notmatch "3\.(9|10|11|12)") {
    Write-Host "[ERROR] Python 3.9+ required. Found: $pyver" -ForegroundColor Red
    exit 1
}
Ok $pyver

# 2. Virtual environment
Log "Creating virtual environment..."
$venvPath = "backend\venv"
if (-not (Test-Path $venvPath)) {
    python -m venv $venvPath
    Ok "Virtual environment created at $venvPath"
} else {
    Ok "Virtual environment already exists"
}

# 3. Install dependencies
Log "Installing Python dependencies..."
& "$venvPath\Scripts\python.exe" -m pip install --upgrade pip --quiet
& "$venvPath\Scripts\pip.exe" install -r backend\requirements.txt --quiet
& "$venvPath\Scripts\pip.exe" install pytest pytest-cov flake8 --quiet
Ok "Dependencies installed"

# 4. Environment file
Log "Setting up .env..."
if (-not (Test-Path "backend\.env")) {
    Copy-Item "backend\.env.example" "backend\.env"
    Warn "Created backend\.env — edit it with your MQTT broker details"
} else {
    Ok ".env already exists"
}

# 5. Run tests
Log "Running test suite..."
& "$venvPath\Scripts\pytest.exe" `
    tests\test_sensor_logic.py `
    tests\test_backend_api.py `
    tests\test_mqtt_client.py `
    -v --tb=short

Write-Host ""
Write-Host "────────────────────────────────────────────"
Ok "Setup complete!"
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Edit backend\.env with your MQTT broker address"
Write-Host "  2. Edit firmware\main\config.h with WiFi + MQTT credentials"
Write-Host "  3. Flash firmware: open firmware\main\main.ino in Arduino IDE"
Write-Host "  4. Start backend:  backend\venv\Scripts\python.exe backend\server.py"
Write-Host "  5. Dashboard:      http://localhost:5000/api/status"
