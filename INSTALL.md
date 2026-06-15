# Installation Guide

## Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Python | 3.9 or higher | 3.11 recommended |
| pip | latest | `python -m pip install --upgrade pip` |
| Git | any | for cloning |

---

## Option A — Simulation Only (No Hardware)

Runs completely on Windows, macOS, or Linux. No Raspberry Pi or GPIO needed.

### 1. Clone the repository

```bash
git clone https://github.com/prashanth-2369002/v2v-intersection-nav.git
cd v2v-intersection-nav
```

### 2. Create and activate a virtual environment

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

**Linux / macOS:**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run a simulation

```bash
python main.py --scenario scenario_1
```

Outputs are saved to `outputs/` (PNG plots) and `data/` (JSON results).

---

## Option B — Raspberry Pi 5 (Full Hardware Mode)

### 1. Hardware setup

Wire components per the GPIO diagram in [README.md](README.md#gpio-wiring-diagram):

- HC-SR04 TRIG → GPIO 23, ECHO → GPIO 24 (via voltage divider)
- L298N IN1–IN4 → GPIO 17, 27, 22, 10; ENA → GPIO 18; ENB → GPIO 13
- OLED SSD1306 → I²C bus 1 (SDA GPIO 2, SCL GPIO 3)

Enable I²C on the Raspberry Pi:
```bash
sudo raspi-config
# → Interface Options → I2C → Enable
```

### 2. Clone and set up

```bash
git clone https://github.com/prashanth-2369002/v2v-intersection-nav.git
cd v2v-intersection-nav
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install RPi.GPIO luma.oled smbus2
```

### 3. Run hardware interface

```bash
python hardware_interface.py --vehicle-id V1 --mode live --duration 60
```

### 4. Run simulation alongside hardware (RSU node)

On the RSU Raspberry Pi:
```bash
python main.py --scenario scenario_1 --visualize False
```

---

## Option C — Development / Testing

```bash
# Install dev dependencies
pip install pytest pytest-cov flake8

# Run all unit tests
python -m pytest tests/ -v

# Run with coverage report
python -m pytest tests/ -v --cov=. --cov-report=term-missing
```

---

## Dependency Details

| Package | Version | Purpose |
|---|---|---|
| `numpy` | ≥ 1.24.0 | Numerical operations |
| `matplotlib` | ≥ 3.8.0 | Plot generation |
| `setuptools` | ≥ 65.0 | Package tooling |
| `pytest` | ≥ 7.0 | Unit testing (dev) |
| `pytest-cov` | ≥ 4.0 | Test coverage (dev) |
| `flake8` | ≥ 6.0 | Linting (dev) |
| `RPi.GPIO` | ≥ 0.7.1 | Raspberry Pi GPIO (hardware only) |
| `luma.oled` | ≥ 3.12.0 | OLED display driver (hardware only) |
| `smbus2` | ≥ 0.4.3 | I²C bus (hardware only) |

---

## Troubleshooting

### `ModuleNotFoundError: No module named 'RPi'`

You are on a non-RPi platform. The hardware interface runs in **stub mode** automatically — no action needed. The simulation stack works normally.

### `matplotlib` display error on headless Linux

Set the non-interactive backend:
```bash
export MPLBACKEND=Agg
python main.py --scenario scenario_1
```

Or in code:
```python
import matplotlib
matplotlib.use('Agg')
```

### `PermissionError` when accessing GPIO

```bash
sudo usermod -aG gpio $USER
# Log out and back in
```

### OLED not showing output

Check I²C address:
```bash
sudo i2cdetect -y 1
# Should show 0x3c in the grid
```

If address differs, set it in `hardware_interface.py`:
```python
OLEDDisplay(i2c_port=1, i2c_address=0x3D)
```

### Plots not saved

Ensure `outputs/` directory exists (created automatically by the simulation):
```bash
mkdir -p outputs data
python main.py --scenario scenario_1
```
