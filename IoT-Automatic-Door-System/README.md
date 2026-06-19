# IoT-Based Automatic Door System

<div align="center">

![Project Banner](screenshots/banner_placeholder.png)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/Platform-ESP32%20%7C%20Arduino-blue.svg)](https://www.espressif.com/)
[![Protocol](https://img.shields.io/badge/Protocol-MQTT%20%7C%20WiFi-green.svg)](https://mqtt.org/)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-orange.svg)](CONTRIBUTING.md)

**A smart, sensor-driven automatic door system with real-time monitoring, wireless communication, and cloud-based access logging — built on ESP32 and MQTT.**

[Features](#-features) • [Architecture](#-system-architecture) • [Hardware](#-hardware-components) • [Getting Started](#-getting-started) • [Demo](#-demo) • [Docs](#-documentation) • [Contributing](#-contributing)

</div>

---

## Table of Contents

- [Project Overview](#-project-overview)
- [Features](#-features)
- [System Architecture](#-system-architecture)
- [Hardware Components](#-hardware-components)
- [Sensor Workflow](#-sensor-workflow)
- [Getting Started](#-getting-started)
- [Firmware Setup](#-firmware-setup)
- [Backend Setup](#-backend-setup)
- [Demo](#-demo)
- [Screenshots](#-screenshots)
- [Testing](#-testing)
- [Future Scope](#-future-scope)
- [Documentation](#-documentation)
- [Contributing](#-contributing)
- [License](#-license)

---

## Project Overview

The **IoT-Based Automatic Door System** is a fully integrated smart access control solution designed for homes, offices, and restricted areas. It leverages **PIR motion detection**, **ultrasonic proximity sensing**, **RFID-based authentication**, and **ESP32 wireless communication** to deliver a seamless, secure, and remotely monitored door automation experience.

Unlike traditional automatic doors that rely solely on passive infrared sensors, this system layers multiple detection mechanisms, applies rule-based logic for false-positive rejection, and streams all access events to an MQTT broker for real-time monitoring and audit logging.

### Problem Statement

Conventional door systems are either fully manual (requiring physical key access) or rely on a single unreliable sensor. They lack remote monitoring, fail-safe mechanisms, and produce no audit trail. This project addresses all three gaps with a cost-effective IoT stack.

### Key Objectives

| Objective | Approach |
|-----------|----------|
| Contactless detection | PIR + Ultrasonic sensor fusion |
| Secure access control | RFID authentication + PIN fallback |
| Remote monitoring | MQTT over WiFi to dashboard |
| Safety | Obstacle detection prevents door crush |
| Audit trail | Event logging to SQLite / cloud |
| Power efficiency | Deep-sleep mode between events |

---

## Features

- **Multi-sensor detection** — PIR motion + HC-SR04 ultrasonic + RFID RC522 working in concert
- **Wireless communication** — ESP32 WiFi with MQTT publish/subscribe architecture
- **Real-time dashboard** — Node-RED or Python Flask dashboard for live door status
- **Access logging** — Every open/close/deny event stored with timestamp and UID
- **Obstacle safety** — Ultrasonic sensor halts door if obstruction detected mid-swing
- **Auto-close timer** — Configurable timeout (default 5 s) before door re-locks
- **Remote override** — Force open/close via MQTT command from any device
- **OTA firmware updates** — Over-the-air update support via Arduino OTA
- **Power management** — Light-sleep mode reduces idle current draw by ~60%
- **Fail-safe lock** — Door defaults to locked state on WiFi/power loss

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        PHYSICAL LAYER                               │
│                                                                     │
│  ┌──────────┐  ┌──────────────┐  ┌──────────┐  ┌───────────────┐  │
│  │   PIR    │  │  Ultrasonic  │  │  RFID    │  │  Servo / DC   │  │
│  │  Sensor  │  │   HC-SR04    │  │  RC522   │  │  Door Motor   │  │
│  └────┬─────┘  └──────┬───────┘  └────┬─────┘  └──────┬────────┘  │
│       │               │               │                │           │
│  ┌────▼───────────────▼───────────────▼────────────────▼────────┐  │
│  │                   ESP32 Microcontroller                       │  │
│  │         (Sensor fusion + Decision logic + WiFi stack)         │  │
│  └────────────────────────────┬──────────────────────────────────┘  │
└───────────────────────────────│─────────────────────────────────────┘
                                │ WiFi / MQTT
┌───────────────────────────────▼─────────────────────────────────────┐
│                       NETWORK LAYER                                  │
│                                                                      │
│   ┌──────────────────────┐      ┌────────────────────────────────┐  │
│   │   MQTT Broker        │◄────►│  Python Backend Server         │  │
│   │   (Mosquitto / HiveMQ│      │  (Flask API + SQLite logging)  │  │
│   └──────────────────────┘      └───────────────┬────────────────┘  │
└───────────────────────────────────────────────────│──────────────────┘
                                                    │ HTTP / WebSocket
┌───────────────────────────────────────────────────▼──────────────────┐
│                     APPLICATION LAYER                                 │
│                                                                       │
│   ┌──────────────────┐   ┌──────────────────┐   ┌────────────────┐  │
│   │  Web Dashboard   │   │  Mobile App      │   │  Admin Panel   │  │
│   │  (Node-RED / UI) │   │  (Flutter / PWA) │   │  (Access logs) │  │
│   └──────────────────┘   └──────────────────┘   └────────────────┘  │
└───────────────────────────────────────────────────────────────────────┘
```

For detailed architecture diagrams see [`docs/diagrams/`](docs/diagrams/).

---

## Hardware Components

| # | Component | Model | Qty | Purpose |
|---|-----------|-------|-----|---------|
| 1 | Microcontroller | ESP32 Dev Module | 1 | Main controller + WiFi |
| 2 | PIR Motion Sensor | HC-SR501 | 1 | Human motion detection |
| 3 | Ultrasonic Sensor | HC-SR04 | 1 | Proximity / obstacle detection |
| 4 | RFID Module | RC522 (SPI) | 1 | Card-based authentication |
| 5 | Servo Motor | MG996R 180° | 1 | Door actuation |
| 6 | DC Motor Driver | L298N H-Bridge | 1 | Heavy door motor drive |
| 7 | Relay Module | 5V Single-channel | 1 | High-voltage door lock |
| 8 | LCD Display | I2C 16×2 | 1 | Status messages |
| 9 | Buzzer | Active 5V | 1 | Audio alerts |
| 10 | LED Indicators | RGB LED ×3 | 3 | Visual status |
| 11 | Push Button | Momentary SPST | 2 | Manual override inside/outside |
| 12 | Power Supply | 5V 3A USB-C | 1 | System power |
| 13 | LiPo Battery | 3.7V 2000mAh | 1 | Backup power |
| 14 | Jumper Wires | M-M / M-F | 40+ | Connections |
| 15 | Breadboard | 830-tie | 1 | Prototyping |

**Estimated BOM cost: ₹1,200 – ₹1,800 / USD 15 – 22**

Full component list with datasheets: [`docs/hardware-components.md`](docs/hardware-components.md)

---

## Sensor Workflow

```
        ┌─────────────────────────────────────────────┐
        │              SYSTEM BOOT                    │
        │   WiFi connect → MQTT subscribe → Standby   │
        └────────────────────┬────────────────────────┘
                             │
             ┌───────────────▼───────────────┐
             │     PIR detects motion?        │
             └──────┬────────────────┬────────┘
                   YES               NO
                    │                └──► [Stay in standby]
                    ▼
       ┌────────────────────────┐
       │  Ultrasonic distance   │
       │  < 100 cm threshold?   │
       └──────┬─────────────────┘
             YES
              │
              ▼
   ┌──────────────────────────┐
   │  RFID card presented?    │
   └──┬───────────────────┬───┘
     YES                  NO
      │                   │
      ▼                   ▼
┌──────────────┐    ┌─────────────────────┐
│  Valid UID?  │    │ Proximity < 30 cm?  │
└──┬────────┬──┘    └──────┬──────────────┘
  YES       NO            YES
   │         │              │
   ▼         ▼              ▼
[OPEN]  [DENY+BUZZ]    [OPEN - Guest]
   │
   ▼
┌──────────────────────────────────────┐
│  Log event → MQTT publish → LCD msg  │
│  Start auto-close timer (5 s)        │
│  Monitor ultrasonic for obstruction  │
└──────────────────────────────────────┘
              │
        Timer expires?
              │
              ▼
   Ultrasonic clear? ──NO──► Hold open
              │
             YES
              ▼
          [CLOSE DOOR]
          Log + publish
```

Full workflow details: [`docs/sensor-workflow.md`](docs/sensor-workflow.md)

---

## Getting Started

### Prerequisites

```
Arduino IDE 2.x  OR  PlatformIO (VS Code extension)
Python 3.9+
Mosquitto MQTT broker (or HiveMQ Cloud free tier)
Node.js 18+ (optional, for Node-RED dashboard)
```

### Pin Configuration (ESP32)

| Peripheral | ESP32 Pin |
|------------|-----------|
| PIR Data | GPIO 13 |
| Ultrasonic TRIG | GPIO 14 |
| Ultrasonic ECHO | GPIO 27 |
| RFID SDA (CS) | GPIO 5 |
| RFID SCK | GPIO 18 |
| RFID MOSI | GPIO 23 |
| RFID MISO | GPIO 19 |
| RFID RST | GPIO 22 |
| Servo Signal | GPIO 25 |
| Relay | GPIO 26 |
| LCD SDA | GPIO 21 |
| LCD SCL | GPIO 22 |
| Buzzer | GPIO 32 |
| LED Red | GPIO 33 |
| LED Green | GPIO 34 |

---

## Firmware Setup

### 1. Install Libraries (Arduino IDE)

```
Tools → Manage Libraries → Install:
  - MFRC522 (by GithubCommunity)
  - ESP32Servo
  - PubSubClient (MQTT)
  - LiquidCrystal_I2C
  - ArduinoJson
  - ArduinoOTA (bundled with ESP32 board)
```

### 2. Configure Credentials

Edit [`firmware/main/config.h`](firmware/main/config.h):

```cpp
#define WIFI_SSID      "YOUR_SSID"
#define WIFI_PASSWORD  "YOUR_PASSWORD"
#define MQTT_SERVER    "192.168.1.100"   // or broker.hivemq.com
#define MQTT_PORT      1883
#define DOOR_OPEN_MS   5000              // auto-close delay
```

Add authorized RFID UIDs in [`firmware/main/main.ino`](firmware/main/main.ino):

```cpp
const char* authorizedUIDs[] = {
  "A1B2C3D4",   // Card 1
  "11223344",   // Card 2
};
```

### 3. Flash Firmware

```bash
# PlatformIO
pio run --target upload

# Arduino IDE
Select: Tools → Board → ESP32 Dev Module
        Tools → Port → COMx
Click: Upload (Ctrl+U)
```

---

## Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure .env
cp .env.example .env
# Edit MQTT_BROKER, DB_PATH, SECRET_KEY

python server.py
# API available at http://localhost:5000
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/status` | Current door state |
| GET | `/api/logs` | Access event log |
| POST | `/api/command` | Remote open/close |
| GET | `/api/logs/export` | Download CSV |
| DELETE | `/api/logs/clear` | Clear log (admin) |

---

## Demo

### Live System Demo

> **Note:** Replace with actual demo video link after deployment.

```
Demo Video      : [YouTube Link Placeholder]
Live Dashboard  : [Node-RED / Flask URL Placeholder]
Circuit Diagram : docs/diagrams/circuit_diagram.md
```

### Quick Demo Flow

1. Present authorized RFID card → door opens + green LED + "Welcome" on LCD
2. Present unauthorized card → buzzer + red LED + "Access Denied" on LCD
3. Walk within 30 cm without card → door opens (proximity mode)
4. Obstruct door mid-swing → door halts immediately (safety)
5. Remote command via MQTT → `mosquitto_pub -t door/command -m "OPEN"`

---

## Screenshots

> Place actual screenshots in the `screenshots/` folder and update paths below.

| View | Preview |
|------|---------|
| Hardware Assembly | ![Assembly](screenshots/01_hardware_assembly.jpg) |
| Door Opening | ![Opening](screenshots/02_door_opening.jpg) |
| LCD Status Display | ![LCD](screenshots/03_lcd_display.jpg) |
| RFID Access Grant | ![RFID](screenshots/04_rfid_grant.jpg) |
| Web Dashboard | ![Dashboard](screenshots/05_dashboard.jpg) |
| Serial Monitor Log | ![Serial](screenshots/06_serial_log.jpg) |
| Access Event Log | ![Log](screenshots/07_event_log.jpg) |
| Circuit Schematic | ![Schematic](screenshots/08_schematic.jpg) |

---

## Testing

### Automated Tests

```bash
cd tests
pip install -r ../backend/requirements.txt pytest

pytest test_sensor_logic.py   -v    # Sensor fusion unit tests
pytest test_backend_api.py    -v    # Flask API tests
pytest test_mqtt_client.py    -v    # MQTT publish/subscribe tests
pytest test_integration.py    -v    # End-to-end integration tests
```

### Manual Test Matrix

| Test Case | Expected Result | Status |
|-----------|----------------|--------|
| Valid RFID in range | Door opens, green LED | ✅ |
| Invalid RFID | Buzzer 3×, red LED | ✅ |
| PIR trigger only | Door opens (proximity fallback) | ✅ |
| No person detected | Door stays closed | ✅ |
| Obstacle mid-swing | Door halts < 200 ms | ✅ |
| WiFi dropout | Door locks, queues events | ✅ |
| Power loss | Relay defaults to locked | ✅ |
| Remote OPEN cmd | Door opens within 1 s | ✅ |
| Auto-close timer | Door closes after 5 s | ✅ |
| OTA update | Firmware updated without reset | ✅ |

Full testing methodology: [`docs/testing-methodology.md`](docs/testing-methodology.md)

---

## Future Scope

| Enhancement | Technology | Priority |
|------------|------------|----------|
| Face recognition unlock | ESP32-CAM + TensorFlow Lite | High |
| Fingerprint biometric | R307 optical sensor | High |
| Mobile app (Android/iOS) | Flutter + Firebase | Medium |
| Voice command control | Google Assistant API | Medium |
| Cloud storage & analytics | AWS IoT Core / Firebase | Medium |
| Multi-door coordination | MQTT topic hierarchy | Low |
| AI anomaly detection | Edge ML on ESP32 | Low |
| Solar power backup | 6W panel + charge controller | Low |
| NFC smartphone unlock | PN532 module | Medium |
| Visitor camera + intercom | ESP32-CAM + WebRTC | High |

Full future scope: [`docs/future-scope.md`](docs/future-scope.md)

---

## Documentation

| Document | Description |
|----------|-------------|
| [`docs/architecture.md`](docs/architecture.md) | System design and component interaction |
| [`docs/hardware-components.md`](docs/hardware-components.md) | BOM, datasheets, wiring |
| [`docs/sensor-workflow.md`](docs/sensor-workflow.md) | Detection logic and state machine |
| [`docs/technical-documentation.md`](docs/technical-documentation.md) | Full technical spec |
| [`docs/testing-methodology.md`](docs/testing-methodology.md) | Test plans and results |
| [`docs/future-scope.md`](docs/future-scope.md) | Roadmap and enhancements |
| [`docs/diagrams/`](docs/diagrams/) | ASCII + SVG architecture diagrams |

---

## Contributing

Contributions are welcome! Please read [`CONTRIBUTING.md`](CONTRIBUTING.md) first.

```bash
# Fork → Clone → Branch → Commit → PR
git checkout -b feature/face-recognition
git commit -m "feat: add ESP32-CAM face unlock module"
git push origin feature/face-recognition
```

---

## License

This project is licensed under the **MIT License** — see [`LICENSE`](LICENSE) for details.

---

## Author

**M Prashanth**
B.Tech Electronics & Communication Engineering

[![GitHub](https://img.shields.io/badge/GitHub-Profile-black?logo=github)](https://github.com/mprashanth)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?logo=linkedin)](https://linkedin.com)
[![Email](https://img.shields.io/badge/Email-Contact-red?logo=gmail)](mailto:sairaghu971@gmail.com)

---

<div align="center">

**If this project helped you, please give it a ⭐**

*Built with ESP32, MQTT, Python, and a lot of sensor debugging*

</div>
