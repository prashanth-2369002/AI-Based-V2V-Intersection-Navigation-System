# System Architecture Diagrams

## 1. High-Level Block Diagram

```
                    ┌─────────────────────────────────────────────────┐
                    │              IoT Door System                     │
                    │                                                  │
  ┌──────────────┐  │  ┌──────────────────────────────────────────┐   │
  │  HC-SR501    │──┼─►│                                          │   │
  │  PIR Sensor  │  │  │            ESP32 DevKit                  │   │
  └──────────────┘  │  │                                          │   │
  ┌──────────────┐  │  │   ┌────────────────────────────────┐    │   │
  │  HC-SR04     │──┼─►│   │       Sensor Fusion Core       │    │   │
  │  Ultrasonic  │  │  │   │                                │    │   │
  └──────────────┘  │  │   │  PIR? → Ultrasonic? → RFID?   │    │   │
  ┌──────────────┐  │  │   │  ↓                             │    │   │
  │  RC522 RFID  │──┼─►│   │  Decision: OPEN / DENY         │    │   │
  │  Module      │  │  │   └─────────────┬──────────────────┘    │   │
  └──────────────┘  │  │                 │                         │   │
                    │  │   ┌─────────────▼──────────────────┐    │   │
  ┌──────────────┐  │  │   │     WiFi + MQTT Stack           │    │   │
  │  MG996R      │◄─┼──│   │  publish: door/event           │    │   │
  │  Servo Motor │  │  │   │  publish: door/status          │    │   │
  └──────────────┘  │  │   │  subscribe: door/command       │    │   │
  ┌──────────────┐  │  │   └────────────────────────────────┘    │   │
  │  Relay Lock  │◄─┼──│                                          │   │
  └──────────────┘  │  └──────────────────────────────────────────┘   │
  ┌──────────────┐  │                        │ WiFi                    │
  │  LCD 16×2    │◄─┼──                      ▼                        │
  └──────────────┘  │          ┌─────────────────────────────┐        │
  ┌──────────────┐  │          │      MQTT Broker             │        │
  │  Buzzer/LEDs │◄─┼──        │   (Mosquitto / HiveMQ)       │        │
  └──────────────┘  │          └──────────────┬──────────────┘        │
                    └─────────────────────────│───────────────────────┘
                                              │
                              ┌───────────────▼──────────────────┐
                              │    Python Flask Backend           │
                              │  • MQTT subscriber (paho)        │
                              │  • SQLite event log              │
                              │  • REST API (:5000)              │
                              └───────────────┬──────────────────┘
                                              │
                    ┌─────────────────────────┼──────────────────────┐
                    ▼                         ▼                       ▼
           ┌──────────────┐        ┌──────────────────┐    ┌──────────────────┐
           │  Web Browser │        │   Mobile App     │    │  MQTT CLI client │
           │  Dashboard   │        │   (Flutter)      │    │  mosquitto_sub   │
           └──────────────┘        └──────────────────┘    └──────────────────┘
```

---

## 2. Circuit Wiring Diagram (ASCII)

```
                       ESP32 DevKit
                    ┌──────────────────┐
            3.3V ───┤ 3V3         GND  ├─── GND (common)
             GND ───┤ GND         D13  ├──── PIR OUT
                    │             D14  ├──── HC-SR04 TRIG
                    │             D27  ├──── HC-SR04 ECHO (via divider)
                    │             D5   ├──── RC522 SDA/CS
                    │             D18  ├──── RC522 SCK
                    │             D23  ├──── RC522 MOSI
                    │             D19  ├──── RC522 MISO
                    │             D22  ├──── RC522 RST / LCD SCL
                    │             D21  ├──── LCD SDA
                    │             D25  ├──── Servo signal (orange)
                    │             D26  ├──── Relay IN
                    │             D32  ├──── Buzzer (+)
                    │             D33  ├──── LED Red anode (220Ω)
                    │             D34  ├──── LED Green anode (220Ω)
                    │             D4   ├──── Button IN (pullup)
                    │             D35  ├──── Button OUT (pullup)
                    └──────────────────┘

HC-SR04 ECHO Voltage Divider:
  ECHO pin → 1kΩ → GPIO27
                  → 2kΩ → GND
  (5V → 3.3V level shift)

Servo Power:
  Red   → External 5V rail (not ESP32 5V — draws too much current)
  Brown → GND (common)
  Orange → GPIO25

Relay:
  VCC → 5V   GND → GND   IN → GPIO26
  COM → Door lock +    NC → Lock power supply
```

---

## 3. MQTT Topic Tree

```
mqtt broker
└── door/
    ├── command       [subscribe] ESP32 listens for OPEN|CLOSE|STATUS
    ├── status        [publish]   JSON: {state, uptime, pir, dist_cm}
    ├── event         [publish]   JSON: {event, uid, reason, uptime_ms}
    └── heartbeat     [publish]   JSON: {uptime, rssi, free_heap}
```

---

## 4. Software Sequence Diagram

```
User          RFID Card    ESP32         MQTT Broker    Flask Backend    Dashboard
  |               |           |                |               |               |
  |── approaches ─►           |                |               |               |
  |               |   PIR HIGH|                |               |               |
  |               |    ───────►               |               |               |
  |               |  ultrasonic: 45cm         |               |               |
  |               |    ───────►               |               |               |
  |── presents ───►           |               |               |               |
  |               │── UID ────►               |               |               |
  |               |   isAuthorized() = true   |               |               |
  |               |    openDoor("rfid")        |               |               |
  |               |── publish ACCESS_GRANTED ──►               |               |
  |               |                            │─── on_msg ───►               |
  |               |                            |               │── log_event() |
  |               |                            |               │── state=OPEN  |
  |               |                            |               │── publish ────►
  |   door opens  |                            |               |    WS update  |
  |◄──────────────|                            |               |               |
  |               |     5s timer fires         |               |               |
  |               |    closeDoor()             |               |               |
  |               |── publish DOOR_CLOSED ─────►               |               |
  |   door closes |                            │─── on_msg ───►               |
  |◄──────────────|                            |               │── log_event() |
  |               |                            |               │── state=CLOSED|
```
