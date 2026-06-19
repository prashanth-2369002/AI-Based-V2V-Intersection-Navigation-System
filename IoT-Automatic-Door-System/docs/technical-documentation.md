# Technical Documentation

## System Specifications

| Parameter | Value |
|-----------|-------|
| Microcontroller | ESP32 (Xtensa LX6 dual-core, 240 MHz) |
| RAM | 520 KB SRAM |
| Flash | 4 MB |
| WiFi | 802.11 b/g/n 2.4 GHz |
| Operating Voltage | 3.3 V (5 V via on-board regulator) |
| MQTT QoS | 1 (at-least-once delivery) |
| Door open time | Configurable, default 5 s |
| Detection range (PIR) | 3–7 m (adjustable) |
| Detection range (Ultrasonic) | 2–400 cm (used: 0–100 cm) |
| RFID frequency | 13.56 MHz (ISO/IEC 14443 Type A) |
| Servo torque | 9.4 kg·cm @ 4.8 V (MG996R) |
| Response latency | < 200 ms (PIR trigger → door begins opening) |
| Offline mode | Events queued; uploaded when reconnected |
| OTA update | ArduinoOTA over UDP/TCP port 3232 |

---

## Firmware Architecture

```
main.ino
├── setup()
│   ├── GPIO init
│   ├── LCD init + splash
│   ├── Servo init (0°)
│   ├── RFID (SPI) init
│   ├── PIR warmup (2 s)
│   ├── WiFi connect
│   ├── MQTT connect + subscribe
│   └── ArduinoOTA init
│
└── loop()
    ├── ArduinoOTA.handle()
    ├── MQTT reconnect (if dropped, every 5 s)
    ├── mqtt.loop()            ← process incoming MQTT messages
    ├── Heartbeat publish      ← every 30 s
    ├── Manual button check    ← debounced
    ├── Auto-close timer check ← obstacle guard
    └── Detection pipeline
        ├── [skip if door not CLOSED]
        ├── PIR read
        ├── [skip if no motion]
        ├── Ultrasonic read (3-sample avg)
        ├── [skip if out of range]
        ├── RFID read (non-blocking)
        └── Decision → openDoor() or deny
```

---

## MQTT Topic Design

```
door/
├── command      → ESP32 subscribes    [OPEN | CLOSE | STATUS]
├── status       ← ESP32 publishes     {state, uptime, pir, dist_cm}
├── event        ← ESP32 publishes     {event, uid, reason, uptime_ms}
└── heartbeat    ← ESP32 publishes     {uptime, rssi, free_heap}
```

**Why retained messages?**  
`door/status` is published with `retain=true` so any new subscriber immediately receives the last known state without waiting for the next poll cycle.

---

## Backend API Reference

### GET /api/status
Returns current door state from in-memory cache (updated by MQTT listener).
```json
{
  "state":      "CLOSED",
  "updated_at": "2024-11-20T14:30:00.123456",
  "uptime":     3600,
  "pir":        0,
  "dist_cm":    85
}
```

### GET /api/logs?limit=100&offset=0&event=ACCESS_GRANTED
Returns paginated event log from SQLite.
```json
[
  {
    "id":        42,
    "timestamp": "2024-11-20T14:25:10.000000",
    "event":     "ACCESS_GRANTED",
    "uid":       "A1B2C3D4",
    "reason":    "rfid",
    "raw_json":  "{...}"
  }
]
```

### POST /api/command
Body: `{"command": "OPEN"}` — publishes to `door/command` MQTT topic.
```json
{"sent": "OPEN"}
```

### GET /api/stats
```json
{
  "total_events":   150,
  "access_granted": 130,
  "access_denied":  20,
  "door_opens":     130,
  "deny_rate":      13.3
}
```

### GET /api/logs/export
Returns CSV download of all events.

### DELETE /api/logs/clear
Requires header `X-Admin-Key: <SECRET_KEY>`. Clears all log records.

---

## Database Schema

```sql
CREATE TABLE events (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp  TEXT    NOT NULL,   -- ISO 8601 UTC
    event      TEXT    NOT NULL,   -- ACCESS_GRANTED, DOOR_OPENED, etc.
    uid        TEXT,               -- RFID UID or empty string
    reason     TEXT,               -- rfid, proximity, remote, button, etc.
    raw_json   TEXT                -- original MQTT payload
);
```

**Indexes (add for production scale):**
```sql
CREATE INDEX idx_events_event     ON events(event);
CREATE INDEX idx_events_timestamp ON events(timestamp);
CREATE INDEX idx_events_uid       ON events(uid);
```

---

## Power Management

The ESP32 supports multiple sleep modes:

| Mode | Current | Wake trigger |
|------|---------|-------------|
| Active (WiFi TX) | 160–240 mA | — |
| Modem sleep | 20 mA | Timer |
| Light sleep | 0.8 mA | GPIO / Timer |
| Deep sleep | 10 µA | Timer / EXT0 |

**Implementation:**  
When no motion is detected for 60 s, the ESP32 enters `esp_light_sleep_start()` with a GPIO wakeup on PIN_PIR. This reduces idle current from ~160 mA to ~1 mA — critical for battery-backed installations.

---

## Error Handling

| Error Condition | Behavior |
|----------------|----------|
| WiFi lost | Queue MQTT events, reconnect every 5 s |
| MQTT broker unreachable | Offline queue (10 messages), retry every 5 s |
| Ultrasonic timeout (-1) | Skip measurement, do not open door |
| RFID read failure | Retry once, then abort (treat as no card) |
| Servo stall | Relay cuts power after 3 s timeout |
| Power loss | Relay defaults to LOW (door locked) |
