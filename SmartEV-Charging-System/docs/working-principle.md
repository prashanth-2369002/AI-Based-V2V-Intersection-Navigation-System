# Working Principle

## Overview

The system operates as a finite state machine running on the ESP32. There are four stable states: **IDLE**, **CHARGING**, **FULL**, and **FAULT**. All transitions are event-driven — either by an RFID card tap or by a sensor threshold breach.

---

## State-by-State Breakdown

### 1. IDLE

The system waits for a card tap. The LCD shows "Tap card to start." The relay is open, so no power flows to the EV port. MQTT telemetry is not published in this state to conserve broker bandwidth.

### 2. Authentication (transition)

When a card is detected on the MFRC522, the ESP32 reads the 4-byte UID over SPI. The UID is compared byte-by-byte against up to four stored UIDs in EEPROM (address 0–15). If there is no match, the buzzer fires one long beep and the LCD shows "Access Denied" for 2 seconds before returning to IDLE. If there is a match, the system transitions to CHARGING.

### 3. CHARGING

On entering CHARGING:
- The relay closes (GPIO 26 goes HIGH), connecting the TP4056 charging module output to the battery pack terminals.
- `bms.resetSession()` clears the energy integrator and sets the session start timestamp.
- `payment.startSession(uid)` records the user UID and start time.
- A `session_start` MQTT event is published.

Every `SENSOR_POLL_INTERVAL_MS` (1000 ms):
1. **INA219** measures bus voltage (pack voltage) and current via I2C.
2. **DS18B20** sensors are requested and read over 1-Wire (takes ~750 ms for 12-bit conversion; triggered in the previous cycle).
3. **SOC** is estimated using a 10-point voltage lookup table with linear interpolation between breakpoints.
4. **Energy integration**: `ΔE = P × Δt`, where `P = V × I` (watts) and `Δt` is the time elapsed since the last poll (in hours). This is accumulated in `_sessionEnergyWh`.
5. **Fault checks** are run on every reading (see below).

Every `MQTT_PUBLISH_INTERVAL_MS` (5000 ms), a JSON telemetry payload is published to `ev/telemetry`:

```json
{
  "uid": "A1B2C3D4",
  "voltage": 11.94,
  "current": 0.842,
  "power_w": 10.05,
  "energy_wh": 2.34,
  "soc": 73.2,
  "temp_c": 32.1,
  "elapsed_s": 837
}
```

### 4. FULL

When SOC reaches 100% (cell voltage ≥ 4.20V/cell), the relay opens automatically. The buzzer plays 3 short beeps. The final bill is calculated and displayed on the LCD for 10 seconds, then the system returns to IDLE. A `session_end` MQTT event is published with energy and cost.

### 5. FAULT

A fault is triggered if any of the following occur during CHARGING:
- **Overvoltage (OVP):** pack voltage / cell count > 4.25V
- **Overtemperature (OTP):** DS18B20 reading > 45°C
- **Overcurrent (OCP):** INA219 current > 4.5A

On fault:
- Relay opens immediately.
- Buzzer fires 3 long beeps.
- The red LED turns on.
- Fault reason string is displayed on the LCD ("OTP: 46.2C", etc.).
- A `fault` MQTT event is published.
- The system waits in FAULT state until a registered card is tapped to acknowledge and reset.

---

## SOC Estimation Method

SOC is estimated using a **voltage-SOC lookup table** derived from a typical 18650 Li-ion discharge curve at 0.5C. The table has 10 breakpoints from 3.00V (0%) to 4.20V (100%) per cell. Between breakpoints, linear interpolation is used.

**Limitation:** Voltage-based SOC is accurate only at low C-rates and with a settled (rested) battery. During active charging, the measured voltage includes an IR drop and is higher than the open-circuit voltage. This means SOC may be slightly over-estimated during charging. For a diploma project, this is an acceptable approximation. A production BMS would use coulomb counting as the primary method with voltage as a calibration reset point.

---

## Payment Calculation

```
Energy (kWh) = accumulated_energy_Wh / 1000
Cost (₹)     = Energy (kWh) × unit_rate (₹/kWh)
```

The unit rate is set in `config.h` (default: ₹8.00/kWh, which is a typical state electricity board commercial tariff). The cost is stored in EEPROM as an unsigned 16-bit integer in paise (1/100 of a Rupee) to avoid floating-point in EEPROM writes.

---

## EEPROM Layout

| Address Range | Content |
|---|---|
| 0 – 15 | Four 4-byte user UIDs (16 bytes total) |
| 16 – 19 | Reserved |
| 20 – 499 | 20 session log entries × 24 bytes each |

Session log entry (24 bytes):
| Offset | Size | Content |
|---|---|---|
| 0 | 4 B | First 4 chars of UID |
| 4 | 2 B | Energy in Wh (uint16) |
| 6 | 2 B | Cost in paise (uint16) |
| 8 | 4 B | Duration in seconds (uint32) |
| 12 | 12 B | Reserved / padding |

---

## Dashboard Data Flow

```
ESP32 → (Wi-Fi) → MQTT Broker (Mosquitto) → (subscribe) → Flask app
                                                              ↓
                                                         SQLite DB
                                                              ↓
                                              Browser → REST /api/* → Chart.js
```

The Flask app runs two concurrent threads: the Flask HTTP server and the MQTT subscriber loop. MQTT messages are handled in the subscriber thread and written to SQLite. The browser polls `/api/live` every 5 seconds for the latest reading and `/api/history` for the chart dataset.

---

## Known Limitations (Prototype)

1. The TP4056 module used for demonstration charges at a maximum of 1A. Real EV charging operates at much higher currents (7A for AC Level 1, 32A+ for AC Level 2) and would require dedicated EVSE hardware with proper safety certifications.
2. The DS18B20 is measuring ambient and approximate cell-pack temperature, not individual cell temperature. A production BMS would use a thermistor per cell.
3. EEPROM on the ESP32 has ~100,000 write cycles. At 20 sessions per slot, this gives a lifetime of ~5 million sessions before wear, which is sufficient for a prototype.
4. The MQTT connection is unauthenticated. A production deployment must use TLS and username/password or certificate-based auth.
