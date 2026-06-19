# Technical Documentation

## Firmware Module Reference

### `config.h`

Central configuration header. All tunable parameters live here so no constant is buried in logic files. Modify this file when deploying to a new environment (different Wi-Fi, MQTT broker IP, or tariff rate).

**Key constants:**

| Constant | Default | Notes |
|---|---|---|
| `WIFI_SSID` | `"YourWiFiSSID"` | Must be 2.4 GHz; ESP32 does not support 5 GHz |
| `MQTT_BROKER` | `"192.168.1.100"` | LAN IP of Mosquitto host |
| `UNIT_RATE_RS` | `8.0` | ₹/kWh; change to match local tariff |
| `TEMP_CUTOFF_C` | `45.0` | IEC 62133-2 recommends ≤60°C; 45°C gives margin |
| `VOLT_CUTOFF_PER_CELL` | `4.25` | 50mV above standard Li-ion 4.20V full threshold |
| `CURRENT_MAX_A` | `4.5` | Just below ACS712-5A rail (5A) to allow headroom |
| `CELL_COUNT` | `3` | 3S pack; adjust if using 2S or 4S |

---

### `BMS` class

**File:** `firmware/src/bms.h`, `bms.cpp`

**Methods:**

| Method | Returns | Description |
|---|---|---|
| `begin()` | `void` | Initialises INA219 and DS18B20 sensors |
| `read()` | `BatteryData` | Polls all sensors, integrates energy, runs fault checks |
| `resetSession()` | `void` | Clears accumulated energy and fault state at session start |
| `getSessionEnergy()` | `float` | Returns Wh accumulated since `resetSession()` |
| `isFaultActive()` | `bool` | True if any protection has tripped |
| `clearFault()` | `void` | Resets fault flag (called after user acknowledges) |

**`BatteryData` struct fields:**

| Field | Type | Unit | Description |
|---|---|---|---|
| `voltage` | `float` | V | Pack voltage (sum of all cells) |
| `current` | `float` | A | Charge current (positive = into battery) |
| `temperature` | `float` | °C | Cell-pack temperature (DS18B20 index 0) |
| `ambientTemp` | `float` | °C | Ambient temperature (DS18B20 index 1) |
| `soc` | `float` | % | Estimated state of charge (0–100) |
| `powerW` | `float` | W | Instantaneous power = V × I |
| `energyWh` | `float` | Wh | Cumulative session energy |
| `isFault` | `bool` | — | True if any threshold exceeded |
| `faultReason` | `char[32]` | — | Human-readable fault string |

---

### `Auth` class

**File:** `firmware/src/auth.h`, `auth.cpp`

**Methods:**

| Method | Returns | Description |
|---|---|---|
| `begin()` | `void` | Calls `EEPROM.begin()` |
| `poll()` | `bool` | Returns true if a registered card was tapped |
| `getLastUID()` | `const char*` | 8-char hex string of last scanned UID |
| `registerUID(uid)` | `bool` | Writes a new UID to the first empty EEPROM slot |

**EEPROM UID storage:** UIDs are stored as 4 raw bytes each, starting at `EEPROM_ADDR_UID_BASE` (address 0). Empty slots contain `0xFF` in all 4 bytes. `registerUID()` finds the first empty slot and writes to it; returns false if all 4 slots are full.

---

### `Payment` class

**File:** `firmware/src/payment.h`, `payment.cpp`

**Methods:**

| Method | Returns | Description |
|---|---|---|
| `startSession(uid)` | `void` | Records start time and user UID |
| `endSession(energyWh)` | `SessionRecord` | Calculates cost, closes the session record |
| `calculateCost(energyWh)` | `float` | Pure function: Wh → ₹ |
| `getElapsedSeconds()` | `unsigned long` | Seconds since session start |
| `isSessionActive()` | `bool` | True between startSession and endSession |
| `logToEEPROM(record)` | `void` | Circular-buffer write to EEPROM |

---

## Backend Module Reference

### `app.py`

Flask application that acts as both MQTT subscriber and HTTP server.

**Routes:**

| Route | Method | Returns | Notes |
|---|---|---|---|
| `/` | GET | HTML | Dashboard page |
| `/api/live` | GET | JSON | Latest `Telemetry` row |
| `/api/history` | GET | JSON array | Last 100 telemetry rows (reversed chronologically for chart) |
| `/api/sessions` | GET | JSON array | Last 50 `session_end` and `fault` events |
| `/api/stats` | GET | JSON | Aggregate totals |

**Database models:**

`Telemetry` — one row per MQTT telemetry message. Columns: `id`, `timestamp`, `uid`, `voltage`, `current_a`, `power_w`, `energy_wh`, `soc`, `temp_c`, `elapsed_s`.

`SessionLog` — one row per session or fault event. Columns: `id`, `uid`, `event`, `energy_wh`, `cost_rs`, `duration_s`, `timestamp`.

---

### `payment_handler.py`

Standalone Python module for payment logic. Importable without Flask context, making it easy to unit-test.

**Functions:**

| Function | Signature | Returns |
|---|---|---|
| `calculate_cost` | `(energy_wh: float, rate: float = 8.0) → float` | Cost in ₹, rounded to 2 dp |
| `estimate_duration_minutes` | `(energy_wh: float, power_w: float) → float` | Estimated charge time in minutes |

**`SessionSummary` dataclass:**

| Property | Type | Description |
|---|---|---|
| `duration` | `timedelta` | `end_time - start_time` |
| `energy_kwh` | `float` | `energy_wh / 1000` |
| `cost_rs` | `float` | Calculated cost |
| `duration_str` | `str` | `HH:MM:SS` formatted string |
| `receipt()` | `str` | Formatted text receipt |

---

## INA219 Calibration Note

The INA219 is configured with `setCalibration_16V_400mA()` in this project because the TP4056 charges at ≤1A. If the charging source is changed to a higher-power supply, call `setCalibration_32V_2A()` (for up to 2A) or implement a custom calibration register value. The Adafruit INA219 library documentation describes the calibration register calculation.

The INA219's shunt resistor (100mΩ on the breakout board) limits measurement to 3.2A before the ADC overflows. For higher currents, the ACS712-5A on GPIO 34 (ADC1 channel) should be used as the primary current sensor instead.

---

## SOC Lookup Table Source

The 10-point voltage-SOC table in `bms.cpp` is adapted from the typical open-circuit voltage (OCV) vs. SOC curve published for Panasonic NCR18650B cells at 25°C, 0.2C discharge rate. The curve is non-linear: it is relatively flat between 3.6V and 4.0V (30%–93%), which means voltage-based SOC has low resolution in the mid-range. This is inherent to Li-ion chemistry and not a software deficiency.

---

## Test Coverage

| File | Tests | Coverage focus |
|---|---|---|
| `test_bms.py` | 12 | SOC interpolation, boundary clamping, fault thresholds |
| `test_payment.py` | 11 | Cost calculation, duration estimation, receipt formatting, edge cases |

Run with: `pytest tests/ -v`
