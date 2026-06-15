# System Overview

## Project Summary

**Title:** AI-Based V2V Negotiation System for Safe Unsignalized Intersection Navigation in EVs  
**Institution:** KL Deemed University (KLEF), Vijayawada  
**Department:** Electrical and Electronics Engineering  
**Year:** 2025–2026  
**Supervisor:** Dr. Pandian, Professor, EEE

---

## Problem Statement

Conventional traffic signals fail to adapt dynamically to real-time vehicle arrivals. At unsignalized intersections, when two or more vehicles converge simultaneously, the risk of collision increases significantly due to:

- Human reaction time delays
- Absence of centralized coordination
- Poor situational awareness across approaching vehicles

---

## Proposed Solution

An AI-assisted, communication-driven intersection management system that:

1. Allows vehicles to **exchange real-time telemetry** (speed, position, ETA) via V2V
2. Uses a **Road-Side Unit** as a neutral coordinator over V2I
3. Applies a **FCFS (First-Come-First-Serve)** priority mechanism with timestamp validation
4. Employs **AI trajectory prediction** to proactively detect and avoid collisions

---

## Technology Stack

| Layer | Technology |
|---|---|
| Compute Platform | Raspberry Pi 5 (OBU + RSU) |
| Communication Protocol | Wi-Fi 802.11ac (simulated 802.11p WAVE) |
| Programming Language | Python 3.9+ |
| AI / ML | Exponential smoothing, physics-based prediction |
| Sensing | HC-SR04 ultrasonic (GPIO trigger/echo) |
| Actuation | L298N H-Bridge + 4× TT gear motors |
| Display | SSD1306 0.96″ I²C OLED |
| Visualization | matplotlib, numpy |
| Testing | pytest |
| CI/CD | GitHub Actions |

---

## System Components

### On-Board Unit (OBU) — per vehicle

Each vehicle carries a Raspberry Pi 5 running:

- `vehicle.py` — state machine and velocity controller
- `communication.py` — V2V broadcaster and V2I uplink client
- `hardware_interface.py` — sensor, motor, and display drivers
- `ai_predictor.py` — local collision risk assessment

### Road-Side Unit (RSU) — at intersection

A dedicated Raspberry Pi 5 running:

- `rsu.py` — vehicle registry and FCFS decision engine
- `fcfs.py` — priority scheduler
- `communication.py` — V2I downlink (priority messages to vehicles)
- `ai_predictor.py` — global trajectory analysis

---

## Performance Metrics

| Metric | Value (Simulated) |
|---|---|
| Priority Assignment Accuracy | 100% across all 3 scenarios |
| Collision Rate | 0% in all test scenarios |
| Average Communication Delay | 50–80 ms |
| Packet Loss Rate | ~2% (configurable) |
| RSU Decision Cycle | Every 0.5 s (5 steps × 0.1 s/step) |
| Simulation Speed | 1000 steps in < 5 s on modern hardware |

---

## Vehicle Information Table (example)

| Vehicle ID | Position (x, y) | Speed (m/s) | Direction | ETA (s) | Status |
|---|---|---|---|---|---|
| V1 | (10, 5) | 15 | North | 8 | Approaching |
| V2 | (12, 7) | 12 | East | 9 | Approaching |

## Priority Assignment Table (example)

| Vehicle ID | Timestamp Received | ETA (s) | Assigned Priority | Action |
|---|---|---|---|---|
| V1 | 12:00:05.235 | 8 | 1 | Proceed |
| V2 | 12:00:05.300 | 9 | 0 | Wait |

---

## Hardware Test Results

| Component | Status |
|---|---|
| Raspberry Pi 5 ↔ L298N Motor Driver | PASS — correct F/B/L/R response |
| Raspberry Pi 5 ↔ HC-SR04 Sensor | PASS — accurate obstacle distance |
| Raspberry Pi 5 ↔ OLED Display | PASS — real-time output, no flicker |
| V2V Wi-Fi Broadcast | PASS — messages received by peer |
| V2I RSU Coordination | PASS — priority assignment delivered |
| FCFS Decision Logic | PASS — 100% priority accuracy |
| AI Collision Prediction | PASS — 0% collision rate in all tests |

---

## Limitations

1. **Tested with 2 vehicles** — scaling to 4+ simultaneous vehicles needs further validation
2. **Simulated communication** — real 802.11p / DSRC hardware not used; Wi-Fi adds ~10 ms extra latency
3. **No GPS integration** — position is simulated; real-world deployment needs GPS or V2X positioning
4. **Simplified AI model** — exponential smoothing is lightweight but not as accurate as LSTM/neural nets
5. **Single intersection** — no multi-intersection coordination or smart-city backend integration

---

## Future Scope

See [future_improvements.md](future_improvements.md) for the full v2.0 roadmap.
