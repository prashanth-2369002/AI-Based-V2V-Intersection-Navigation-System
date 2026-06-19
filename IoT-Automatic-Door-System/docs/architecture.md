# System Architecture

## Overview

The system is organized into three tiers that mirror the classic IoT stack:

```
Physical Layer   →   Network Layer   →   Application Layer
(Sensors/MCU)        (MQTT/WiFi)         (API/Dashboard/DB)
```

## Component Interaction Diagram

```
┌───────────────────────────────────────────────────────────────────────────┐
│  PHYSICAL LAYER                                                           │
│                                                                           │
│  HC-SR501 (PIR)   ──→ ┐                                                  │
│  HC-SR04 (Ultrasonic) ─┤→  ESP32 DevKit                                  │
│  RC522 (RFID)     ──→ ┘     │  ├── Sensor fusion logic                   │
│                              │  ├── State machine (CLOSED/OPENING/OPEN)   │
│  MG996R Servo     ←── ───────┘  ├── MQTT publish (door/event, door/status)│
│  Relay (Lock)     ←──           ├── MQTT subscribe (door/command)         │
│  I2C LCD          ←──           └── OTA firmware update listener          │
│  Buzzer + LEDs    ←──                                                      │
└───────────────────────────────────────────────────────────────────────────┘
                               │ 802.11 b/g/n (2.4 GHz)
                               ▼
┌───────────────────────────────────────────────────────────────────────────┐
│  NETWORK LAYER                                                            │
│                                                                           │
│  ┌─────────────────────────────┐                                          │
│  │  Mosquitto MQTT Broker      │  Topics:                                 │
│  │  (Raspberry Pi / VPS)       │  • door/event   ← ESP32 publishes        │
│  │                             │  • door/status  ← ESP32 publishes        │
│  │  Port 1883 (plain)          │  • door/command → ESP32 subscribes       │
│  │  Port 8883 (TLS optional)   │  • door/heartbeat ← ESP32 publishes      │
│  └──────────────┬──────────────┘                                          │
│                 │ paho-mqtt subscribe                                      │
│  ┌──────────────▼──────────────┐                                          │
│  │  Python Flask Backend       │  Endpoints:                              │
│  │  (server.py)                │  GET  /api/status                        │
│  │                             │  GET  /api/logs                          │
│  │  SQLite (door_events.db)    │  POST /api/command                       │
│  │  Background MQTT listener   │  GET  /api/logs/export                   │
│  └─────────────────────────────┘  GET  /api/stats                         │
└───────────────────────────────────────────────────────────────────────────┘
                               │ HTTP REST / WebSocket
                               ▼
┌───────────────────────────────────────────────────────────────────────────┐
│  APPLICATION LAYER                                                        │
│                                                                           │
│  ┌──────────────────┐   ┌────────────────────┐   ┌────────────────────┐  │
│  │  Web Dashboard   │   │  Mobile App        │   │  CLI / MQTT client │  │
│  │  (Node-RED UI /  │   │  (Flutter PWA)     │   │  (mosquitto_pub)   │  │
│  │   Flask + HTML)  │   │                    │   │                    │  │
│  │                  │   │  • Push alerts     │   │  mosquitto_pub     │  │
│  │  • Live status   │   │  • Remote open     │   │    -t door/command │  │
│  │  • Event log     │   │  • Access history  │   │    -m "OPEN"       │  │
│  │  • Stats charts  │   │  • UID management  │   │                    │  │
│  └──────────────────┘   └────────────────────┘   └────────────────────┘  │
└───────────────────────────────────────────────────────────────────────────┘
```

## State Machine

```
                  ┌───────────┐
           ┌─────►│  CLOSED   │◄──────────────────────────────┐
           │      └─────┬─────┘                               │
           │            │ Sensor trigger / Remote cmd          │
           │            ▼                                      │
           │      ┌───────────┐                               │
           │      │  OPENING  │── Obstacle? ──► [HOLD/REVERSE]│
           │      └─────┬─────┘                               │
           │            │ Servo reached 90°                    │
           │            ▼                                      │
           │      ┌───────────┐                               │
           │      │   OPEN    │── Timer + no obstacle ────────►│
           │      └─────┬─────┘          CLOSING               │
           │            │ Auto-close / Remote cmd               │
           │            ▼                                      │
           │      ┌───────────┐                               │
           └──────│  CLOSING  │── Obstacle ──► [REOPEN]       │
                  └───────────┘                               │
                        │ Servo reached 0°                    │
                        └────────────────────────────────────►┘
```

## Data Flow

```
Event timeline for authorized RFID scan:

T+0ms    PIR HIGH → starts detection pipeline
T+5ms    Ultrasonic read: 45 cm (within 100 cm trigger zone)
T+10ms   RFID: card detected, UID = "A1B2C3D4"
T+12ms   isAuthorized("A1B2C3D4") → true
T+12ms   openDoor("rfid") called
T+12ms   publishEvent("ACCESS_GRANTED", "A1B2C3D4", "rfid")
T+15ms   MQTT publish → door/event JSON
T+15ms   Flask backend receives → log_event() → SQLite INSERT
T+150ms  Servo sweep 0°→90° complete
T+150ms  doorState = DOOR_OPEN
T+150ms  publishStatus() → door/status OPEN
T+5150ms Auto-close timer fires
T+5155ms Ultrasonic clear → closeDoor()
T+5305ms Servo sweep 90°→0° complete
T+5305ms Relay LOW → lock engaged
T+5305ms publishEvent("DOOR_CLOSED", "SYSTEM", "auto_close")
```

## Security Considerations

| Threat | Mitigation |
|--------|-----------|
| RFID cloning | Use DESFire EV2 cards (AES-128) instead of Mifare Classic |
| MQTT eavesdropping | TLS on port 8883 + username/password auth |
| Remote command spoofing | JWT-signed commands or MQTT ACL |
| Relay bypass | Physical lock on door frame independent of software |
| WiFi credential exposure | Store in NVS partition, not flash |
| OTA hijack | Password-protected OTA + code signing (future) |
