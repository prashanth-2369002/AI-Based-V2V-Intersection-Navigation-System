# Testing Methodology

## Test Strategy

The project follows a three-tier testing pyramid:

```
        ┌──────────────────────────┐
        │    Integration Tests     │  ← Real MQTT + Flask API
        │  (test_integration.py)   │
        ├──────────────────────────┤
        │     API / Unit Tests     │  ← Flask routes + in-memory DB
        │  (test_backend_api.py)   │
        ├──────────────────────────┤
        │   Logic / Unit Tests     │  ← Pure Python decision logic
        │ (test_sensor_logic.py)   │
        └──────────────────────────┘
```

---

## Automated Test Cases

### Sensor Logic (`test_sensor_logic.py`)

| Test | Input | Expected |
|------|-------|----------|
| No PIR | pir=False, any distance | No open |
| PIR + out of range | pir=True, 150 cm | No open |
| Sensor timeout | pir=True, -1 cm | No open |
| Valid RFID | pir=True, 50 cm, UID=A1B2C3D4 | Open (rfid) |
| All 3 authorized UIDs | each UID | All open |
| Unauthorized RFID | pir=True, 50 cm, UID=BADC0FFE | Deny |
| Proximity ≤ 30 cm | pir=True, 25 cm, no RFID | Open (proximity) |
| Proximity = 30 cm boundary | pir=True, 30 cm, no RFID | Open |
| Proximity > 30 cm | pir=True, 31 cm, no RFID | No open |
| Obstacle at 5 cm | dist=5 | is_obstacle=True |
| No obstacle at 15 cm | dist=15 | is_obstacle=False |
| RFID takes priority over proximity | pir=True, 10 cm, valid UID | Open (rfid) |
| Denied RFID blocks proximity | pir=True, 10 cm, bad UID | Deny |

### Backend API (`test_backend_api.py`)

| Test | Endpoint | Expected |
|------|----------|----------|
| Status returns state | GET /api/status | 200 + JSON with "state" |
| Empty log | GET /api/logs | 200 + [] |
| Log and retrieve | POST log + GET /api/logs | Event in list |
| Filter by event type | GET /api/logs?event=X | Only matching events |
| Pagination | GET /api/logs?limit=2 | 2 results max |
| Invalid command | POST /api/command EXPLODE | 400 |
| Clear without auth | DELETE /api/logs/clear | 401 |
| Clear with auth | DELETE + X-Admin-Key | 200 + empty log |
| Stats calculation | Mixed events | Correct counts + deny_rate |
| CSV export | GET /api/logs/export | CSV with headers |

---

## Manual Hardware Test Matrix

### Functional Tests

| # | Test Case | Procedure | Expected Result | Pass? |
|---|-----------|-----------|----------------|-------|
| F01 | Boot sequence | Power on | LCD splash → "Door Ready" | |
| F02 | Valid RFID open | Present authorized card within 50 cm | Green LED + door opens | |
| F03 | Invalid RFID deny | Present unknown card | Red LED + 3× buzzer | |
| F04 | Proximity open | Walk within 25 cm (no card) | Door opens | |
| F05 | Auto-close | Open door, stand back | Door closes after 5 s | |
| F06 | Auto-close reset | Open door, put hand at 5 cm | Timer resets, door holds | |
| F07 | Manual button (inside) | Press inside button | Door toggles open/close | |
| F08 | Manual button (outside) | Press outside button | Door opens | |
| F09 | Remote OPEN | `mosquitto_pub -t door/command -m "OPEN"` | Door opens within 1 s | |
| F10 | Remote CLOSE | `mosquitto_pub -t door/command -m "CLOSE"` | Door closes within 1 s | |
| F11 | Obstacle safety | Open door, place object at 5 cm during swing | Door halts immediately | |
| F12 | Event logging | Perform F02 | Event appears in /api/logs | |
| F13 | Dashboard update | Perform F09 | Dashboard shows OPEN | |
| F14 | OTA update | Upload new binary via Arduino IDE | Firmware updates, reboots | |

### Reliability Tests

| # | Test | Method | Pass Criteria |
|---|------|--------|--------------|
| R01 | WiFi dropout recovery | Pull ethernet from router for 30 s | Reconnects within 10 s of restore |
| R02 | MQTT broker restart | Stop mosquitto, restart | Reconnects + drains queue |
| R03 | Power cycle | Cut and restore 5V | System recovers to CLOSED state |
| R04 | Rapid card presentation | Scan 10 cards in 10 s | All events logged, no crash |
| R05 | 24-hour soak test | Leave running for 24 h | No reboot, memory stable |
| R06 | PIR false positive rate | Leave idle 1 h with no humans | < 2 false triggers per hour |

### Performance Tests

| Metric | Target | Measured |
|--------|--------|---------|
| PIR → door begin (latency) | < 200 ms | TBD |
| RFID read time | < 50 ms | TBD |
| Ultrasonic sample (×3 avg) | < 100 ms | TBD |
| MQTT publish latency (LAN) | < 50 ms | TBD |
| Servo sweep time (0°→90°) | ~1.35 s | TBD |
| WiFi reconnect time | < 10 s | TBD |

---

## Running Tests

```bash
# Install test dependencies
pip install pytest flask paho-mqtt

# All tests
cd IoT-Automatic-Door-System
pytest tests/ -v

# Specific suite
pytest tests/test_sensor_logic.py -v
pytest tests/test_backend_api.py  -v

# With coverage report
pip install pytest-cov
pytest tests/ --cov=backend --cov-report=html
open htmlcov/index.html
```

---

## CI Pipeline

See [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) for automated test execution on every push.

The pipeline:
1. Installs Python dependencies
2. Runs `pytest tests/` with coverage
3. Reports pass/fail per commit
