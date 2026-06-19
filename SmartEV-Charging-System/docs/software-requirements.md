# Software Requirements

## Development Environment

| Tool | Version | Platform | Purpose |
|---|---|---|---|
| Arduino IDE | 2.3.x | Win/Mac/Linux | Firmware development and flashing |
| Python | 3.9 – 3.12 | Win/Mac/Linux | Dashboard backend |
| Git | 2.40+ | Any | Version control |
| Mosquitto | 2.0.x | Win/Mac/Linux | Local MQTT broker |
| SQLite Browser | 3.12+ | Any | Inspect session database (optional) |
| VS Code | 1.90+ | Any | Recommended code editor |

---

## Firmware Dependencies (Arduino / ESP32)

Install all libraries via **Arduino IDE → Tools → Manage Libraries** or via the PlatformIO library registry.

### Board Support Package

```
Board Manager URL: https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
Package: esp32 by Espressif Systems
Version: 2.0.14
```

**Arduino IDE Board Settings:**

| Setting | Value |
|---|---|
| Board | ESP32 Dev Module |
| Upload Speed | 115200 |
| CPU Frequency | 240 MHz (WiFi/BT) |
| Flash Frequency | 80 MHz |
| Flash Mode | QIO |
| Flash Size | 4 MB (32 Mb) |
| Partition Scheme | Default 4MB with spiffs |
| Core Debug Level | None |
| PSRAM | Disabled |
| Port | (your COM port) |

---

### Required Libraries

| Library | Version | Author | Install via |
|---|---|---|---|
| MFRC522 | 1.4.10 | miguelbalboa | Library Manager |
| Adafruit INA219 | 1.2.3 | Adafruit | Library Manager |
| Adafruit BusIO | 1.16.1 | Adafruit | Library Manager (dependency of INA219) |
| OneWire | 2.3.7 | Paul Stoffregen | Library Manager |
| DallasTemperature | 3.9.0 | Miles Burton | Library Manager |
| LiquidCrystal\_I2C | 1.1.3 | Frank de Brabander | Library Manager |
| PubSubClient | 2.8.0 | Nick O'Leary | Library Manager |
| ArduinoJson | 6.21.3 | Benoit Blanchon | Library Manager |

**Built-in (no install needed):**
- `WiFi.h` — included in ESP32 Arduino core
- `SPI.h` — included in Arduino core
- `Wire.h` — included in Arduino core
- `EEPROM.h` — included in ESP32 Arduino core

---

### Verifying Library Versions

After installing, confirm versions in `Arduino IDE → Sketch → Include Library → Manage Libraries` and check the version column. Version mismatches between ArduinoJson v5 and v6 are a common source of compile errors — this project uses v6 syntax (`StaticJsonDocument`, not `StaticJsonBuffer`).

---

## Backend Dependencies (Python)

### Installation

```bash
# From the project root
cd software

python -m venv venv

# Activate:
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate.bat       # Windows cmd
venv\Scripts\Activate.ps1       # Windows PowerShell

pip install -r requirements.txt
```

### `requirements.txt`

```
Flask==3.0.3
flask-mqtt==1.1.1
Flask-SQLAlchemy==3.1.1
paho-mqtt==1.6.1
python-dotenv==1.0.1
pytest==8.2.0
pytest-flask==1.3.0
```

### Package Roles

| Package | Role |
|---|---|
| Flask | HTTP server and template rendering |
| flask-mqtt | MQTT subscriber integrated with Flask app context |
| Flask-SQLAlchemy | ORM — maps Python classes to SQLite tables |
| paho-mqtt | Underlying MQTT client used by flask-mqtt |
| python-dotenv | Loads `.env` file into `os.environ` |
| pytest | Test runner |
| pytest-flask | Flask test client fixture for API tests |

---

## Environment Variables (`.env`)

Create a `.env` file in `software/dashboard/` (never commit this file):

```env
# MQTT broker
MQTT_BROKER=127.0.0.1
MQTT_PORT=1883

# Database
DATABASE_URL=sqlite:///ev_charging.db

# Tariff
UNIT_RATE_RS=8.0

# Flask
FLASK_ENV=development
SECRET_KEY=change-this-to-a-random-string
```

A `.env.example` with placeholder values is committed in the repository.

---

## MQTT Broker Setup (Mosquitto)

### Install

```bash
# Ubuntu / Debian
sudo apt update && sudo apt install mosquitto mosquitto-clients -y
sudo systemctl enable mosquitto
sudo systemctl start mosquitto

# Windows — download installer from https://mosquitto.org/download/
# macOS
brew install mosquitto
brew services start mosquitto
```

### Verify Broker

```bash
# In one terminal — subscribe to all EV topics
mosquitto_sub -h 127.0.0.1 -t "ev/#" -v

# In another terminal — publish a test message
mosquitto_pub -h 127.0.0.1 -t "ev/test" -m '{"hello":"world"}'
```

If the subscriber terminal shows the message, the broker is working.

### Default Mosquitto Config

The default Mosquitto 2.x config (`/etc/mosquitto/mosquitto.conf`) does not allow anonymous connections. Add these lines to enable local anonymous access (for development only):

```
# /etc/mosquitto/mosquitto.conf
listener 1883 127.0.0.1
allow_anonymous true
```

Restart after editing: `sudo systemctl restart mosquitto`

---

## Running Tests

```bash
cd SmartEV-Charging-System

# Install test dependencies (if not already done)
pip install -r software/requirements.txt

# Run all tests
pytest tests/ -v

# Run a specific test file
pytest tests/test_bms.py -v

# Run with coverage report
pip install pytest-cov
pytest tests/ --cov=software --cov-report=term-missing
```

Expected output — all tests should pass:

```
tests/test_bms.py::TestSOCBoundaries::test_empty_battery         PASSED
tests/test_bms.py::TestSOCBoundaries::test_below_empty_clamps_to_zero  PASSED
tests/test_bms.py::TestSOCBoundaries::test_full_battery          PASSED
tests/test_bms.py::TestSOCBoundaries::test_above_full_clamps_to_100    PASSED
tests/test_bms.py::TestSOCInterpolation::test_midpoint_3v2_to_3v4     PASSED
tests/test_bms.py::TestSOCInterpolation::test_midpoint_3v6_to_3v7     PASSED
tests/test_bms.py::TestSOCInterpolation::test_exact_table_values       PASSED
tests/test_bms.py::TestSOCInterpolation::test_soc_monotonically_increasing PASSED
tests/test_bms.py::TestSOCInterpolation::test_soc_always_in_range      PASSED
tests/test_bms.py::TestFaultThresholds::test_overvoltage_trip          PASSED
tests/test_bms.py::TestFaultThresholds::test_no_overvoltage_below_limit PASSED
tests/test_bms.py::TestFaultThresholds::test_overtemp_trip             PASSED
tests/test_bms.py::TestFaultThresholds::test_no_overtemp_at_limit      PASSED
tests/test_bms.py::TestFaultThresholds::test_overcurrent_trip          PASSED
tests/test_bms.py::TestFaultThresholds::test_overcurrent_safe          PASSED
tests/test_payment.py::TestCalculateCost::test_zero_energy_is_zero_cost PASSED
...
======================== 26 passed in 0.42s ========================
```

---

## Simulation (Without Hardware)

If hardware is not available, the firmware logic can be simulated using **Wokwi** (free, browser-based ESP32 simulator):

1. Go to [wokwi.com](https://wokwi.com) and create a new ESP32 project.
2. Add components: MFRC522, LCD (I2C), and a resistor + LED for the relay indicator.
3. Copy `firmware/src/*.ino`, `*.h`, and `*.cpp` files into the Wokwi editor.
4. See `simulation/README.md` for the Wokwi JSON diagram configuration.

The Python dashboard can be run locally and tested independently using the test MQTT publisher script in `simulation/mqtt_simulator.py`.
