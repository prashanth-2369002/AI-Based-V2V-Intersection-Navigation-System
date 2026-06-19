#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# IoT Automatic Door System — Backend Setup Script (Linux / macOS / WSL)
# Usage: bash scripts/setup.sh
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

CYAN='\033[0;36m'; GREEN='\033[0;32m'; RED='\033[0;31m'; NC='\033[0m'

log()  { echo -e "${CYAN}[SETUP]${NC} $*"; }
ok()   { echo -e "${GREEN}[OK]${NC} $*"; }
err()  { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }

log "IoT Automatic Door System — Backend Setup"
echo "────────────────────────────────────────────"

# 1. Python version check
log "Checking Python version..."
python3 --version | grep -E "3\.(9|10|11|12)" > /dev/null \
    || err "Python 3.9+ required. Found: $(python3 --version)"
ok "Python OK"

# 2. Virtual environment
log "Creating virtual environment..."
if [ ! -d "backend/venv" ]; then
    python3 -m venv backend/venv
    ok "Virtual environment created at backend/venv"
else
    ok "Virtual environment already exists"
fi

# 3. Activate and install
log "Installing Python dependencies..."
source backend/venv/bin/activate
pip install --upgrade pip --quiet
pip install -r backend/requirements.txt --quiet
pip install pytest pytest-cov flake8 --quiet
ok "Dependencies installed"

# 4. Environment file
log "Setting up .env..."
if [ ! -f "backend/.env" ]; then
    cp backend/.env.example backend/.env
    log "Created backend/.env — edit it with your MQTT broker details"
else
    ok ".env already exists"
fi

# 5. Mosquitto check
log "Checking for MQTT broker (Mosquitto)..."
if command -v mosquitto &> /dev/null; then
    ok "Mosquitto found: $(mosquitto -h 2>&1 | head -1)"
else
    log "Mosquitto not found. Install it:"
    echo "    Ubuntu/Debian : sudo apt install mosquitto mosquitto-clients"
    echo "    macOS         : brew install mosquitto"
    echo "    Or use HiveMQ Cloud free tier: https://www.hivemq.com/mqtt-cloud-broker/"
fi

# 6. Run tests
log "Running test suite..."
cd "$(dirname "$0")/.."
pytest tests/test_sensor_logic.py tests/test_backend_api.py tests/test_mqtt_client.py \
    -v --tb=short 2>&1 | tail -20
ok "Tests complete"

echo ""
echo "────────────────────────────────────────────"
ok "Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit backend/.env with your MQTT broker address"
echo "  2. Edit firmware/main/config.h with WiFi credentials + MQTT broker"
echo "  3. Flash firmware: open firmware/main/main.ino in Arduino IDE"
echo "  4. Start backend: source backend/venv/bin/activate && python backend/server.py"
echo "  5. Dashboard:     http://localhost:5000/api/status"
