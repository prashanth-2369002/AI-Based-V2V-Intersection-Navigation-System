<<<<<<< HEAD
# AI-Based V2V Negotiation System for Safe Unsignalized Intersection Navigation in EVs

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)
![Platform](https://img.shields.io/badge/Platform-Raspberry%20Pi%205-red?style=for-the-badge&logo=raspberry-pi)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge)
![CI](https://img.shields.io/badge/CI-GitHub%20Actions-orange?style=for-the-badge&logo=github-actions)

**Final-year B.Tech Engineering Project — KL Deemed University (KLEF), 2025–2026**

[Overview](#overview) • [Architecture](#system-architecture) • [Hardware](#hardware-components) • [Installation](#installation) • [Usage](#usage) • [Results](#results) • [Docs](#documentation) • [License](#license)

</div>

---

## Overview

This project presents an **AI-based navigation system** for four-way unsignalized intersections, designed for Electric Vehicles (EVs). When two or more vehicles approach simultaneously, the system coordinates right-of-way using:

- **Vehicle-to-Vehicle (V2V) communication** — vehicles share speed, position, direction, and ETA in real time
- **Vehicle-to-Infrastructure (V2I) communication** — a Road-Side Unit (RSU) acts as a central coordinator
- **FCFS priority algorithm** — First-Come-First-Serve scheduling backed by timestamp validation
- **AI trajectory prediction** — exponential-smoothing-based collision risk scoring with proactive avoidance

The hardware prototype uses **Raspberry Pi 5** as the compute core, **HC-SR04** ultrasonic sensors for obstacle detection, an **L298N** motor driver for wheel control, and an **OLED display** for real-time status output.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    INTERSECTION ZONE                            │
│                                                                 │
│   Vehicle V1 (OBU)              Vehicle V2 (OBU)               │
│   ┌──────────────┐              ┌──────────────┐               │
│   │ Raspberry Pi │◄─── V2V ───►│ Raspberry Pi │               │
│   │ HC-SR04      │              │ HC-SR04      │               │
│   │ L298N Motor  │              │ L298N Motor  │               │
│   │ OLED Display │              │ OLED Display │               │
│   └──────┬───────┘              └──────┬───────┘               │
│          │ V2I (Wi-Fi / 802.11p)       │ V2I                   │
│          ▼                             ▼                        │
│   ┌────────────────────────────────────────┐                   │
│   │         Road-Side Unit (RSU)           │                   │
│   │         Raspberry Pi 5                 │                   │
│   │                                        │                   │
│   │  ┌──────────┐  ┌──────────────────┐   │                   │
│   │  │   FCFS   │  │  AI Trajectory   │   │                   │
│   │  │Scheduler │  │   Predictor      │   │                   │
│   │  └──────────┘  └──────────────────┘   │                   │
│   └────────────────────────────────────────┘                   │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
Vehicle broadcasts →  V2V Channel  → Other Vehicles (peer awareness)
Vehicle sends      →  V2I Channel  → RSU (registration + telemetry)
RSU processes      →  FCFS + AI    → Priority Decision
RSU sends          →  V2I Channel  → Vehicle (can_cross = True/False)
Vehicle acts       →  Motor Driver → Physical movement / speed control
```

---

## Key Features

| Feature | Description |
|---|---|
| **V2V Communication** | Real-time peer-to-peer message exchange between vehicles |
| **V2I Communication** | RSU-mediated vehicle–infrastructure coordination |
| **FCFS Priority** | Timestamp-validated first-come-first-serve scheduling |
| **AI Prediction** | Exponential-smoothing trajectory predictor with risk scoring |
| **Collision Avoidance** | Proactive deceleration triggered by predicted risk score |
| **Multi-scenario** | 3 built-in test scenarios (normal, latency, close-arrival) |
| **Evaluation Metrics** | Precision, recall, F1, latency, throughput, RMSE |
| **Visualization** | 6 auto-generated plot types saved to `outputs/` |
| **Hardware Interface** | GPIO, ultrasonic sensor, motor, OLED abstraction layer |
| **Dataset Generator** | Synthetic CSV dataset for ML training and benchmarking |

---

## Hardware Components

| Component | Model | Role |
|---|---|---|
| Microcomputer | Raspberry Pi 5 (4 GB / 8 GB) | Main compute + networking |
| Distance Sensor | HC-SR04 Ultrasonic | Obstacle detection (trigger/echo GPIO) |
| Motor Driver | L298N Dual H-Bridge | 4× TT gear motor speed/direction control |
| Display | 0.96″ I²C OLED (SSD1306) | Real-time distance + status output |
| Motors | Yellow TT Gear Motors (×4) | Differential-drive locomotion |
| Battery | 18650 Li-Ion (7.4 V pack) | System power supply |
| Network | Wi-Fi 802.11ac (built-in RPi 5) | V2V / V2I wireless link |

### GPIO Wiring Diagram

```
HC-SR04  →  RPi GPIO
  VCC    →  5V  (Pin 2)
  GND    →  GND (Pin 6)
  TRIG   →  GPIO 23 (Pin 16)
  ECHO   →  GPIO 24 (Pin 18)  [via 1kΩ / 2kΩ voltage divider]

L298N    →  RPi GPIO
  IN1    →  GPIO 17 (Pin 11)
  IN2    →  GPIO 27 (Pin 13)
  IN3    →  GPIO 22 (Pin 15)
  IN4    →  GPIO 10 (Pin 19)
  ENA    →  GPIO 18 (PWM0)
  ENB    →  GPIO 13 (PWM1)

OLED SSD1306  →  RPi I²C
  VCC          →  3.3V (Pin 1)
  GND          →  GND  (Pin 9)
  SCL          →  GPIO 3 / SCL1 (Pin 5)
  SDA          →  GPIO 2 / SDA1 (Pin 3)
```

---

## Folder Structure

```
v2v-intersection-nav/
│
├── .github/
│   └── workflows/
│       └── ci.yml               # GitHub Actions CI pipeline
│
├── docs/
│   ├── architecture.md          # Detailed system architecture
│   ├── uml_diagram.md           # UML class diagrams (Mermaid)
│   ├── sequence_diagram.md      # Message sequence diagrams
│   ├── system_overview.md       # High-level system overview
│   └── future_improvements.md   # Roadmap & future scope
│
├── tests/
│   ├── __init__.py
│   ├── test_rsu.py              # RSU + FCFS unit tests
│   ├── test_communication.py    # V2V/V2I channel tests
│   ├── test_ai_predictor.py     # Trajectory predictor tests
│   └── test_fcfs.py             # FCFS scheduler tests
│
├── data/                        # Simulation JSON outputs (auto-created)
│   └── .gitkeep
│
├── outputs/                     # Generated plot PNGs (auto-created)
│   └── .gitkeep
│
├── config.py                    # All tunable parameters
├── vehicle.py                   # Vehicle OBU model
├── rsu.py                       # Road-Side Unit + FCFS coordination
├── communication.py             # V2V / V2I wireless channel simulation
├── ai_predictor.py              # Trajectory prediction + collision risk
├── fcfs.py                      # Standalone FCFS scheduling module
├── simulation.py                # Main simulation engine (orchestrator)
├── visualizer.py                # Plot generation (matplotlib)
├── hardware_interface.py        # Raspberry Pi GPIO / sensor abstraction
├── evaluation.py                # Metrics: precision, recall, F1, RMSE
├── dataset_generator.py         # Synthetic dataset creation script
├── main.py                      # CLI entry point
│
├── requirements.txt
├── INSTALL.md
├── LICENSE
└── README.md
```

---

## Installation

See [INSTALL.md](INSTALL.md) for full step-by-step instructions.

**Quick start (simulation only — no hardware required):**

```bash
git clone https://github.com/prashanth-2369002/v2v-intersection-nav.git
cd v2v-intersection-nav

python -m venv venv
# Windows:
venv\Scripts\activate
# Linux / macOS:
source venv/bin/activate

pip install -r requirements.txt
python main.py --scenario scenario_1
```

---

## Usage

### Run a Simulation Scenario

```bash
# Two vehicles, perpendicular approach (default)
python main.py --scenario scenario_1

# Four vehicles, mixed speeds
python main.py --scenario scenario_2

# Emergency vehicle priority simulation
python main.py --scenario scenario_3

# Disable auto-visualization (faster batch runs)
python main.py --scenario scenario_1 --visualize False
```

### Generate a Synthetic Dataset

```bash
python dataset_generator.py --samples 1000 --output data/dataset.csv
```

### Evaluate Model Performance

```bash
python evaluation.py --results data/simulation_scenario_1_<timestamp>.json
```

### Run All Unit Tests

```bash
python -m pytest tests/ -v
```

### Hardware Mode (Raspberry Pi only)

```bash
python hardware_interface.py --mode live
```

---

## Results

### Simulation Benchmark (3 scenarios)

| Scenario | Vehicles | Avg Comm Delay | Collision Risk | Priority Accuracy |
|---|---|---|---|---|
| Normal approach | 2 | 50 ms | 0 % | 100 % |
| High network latency | 2 | 80 ms | 0 % | 100 % |
| Near-simultaneous arrival | 2 | 60 ms | 0 % | 100 % |

### Generated Plots (`outputs/`)

| File | Description |
|---|---|
| `trajectories.png` | Vehicle paths through the intersection |
| `velocity_profile.png` | Speed over time per vehicle |
| `communication_delay.png` | V2V / V2I message statistics |
| `collision_risk.png` | Risk score events and distribution |
| `predicted_vs_actual.png` | AI prediction accuracy overlay |
| `performance_metrics.png` | Crossing success, wait time, collision stats |

### Console Output Sample

```
AI-BASED V2V NEGOTIATION SYSTEM FOR INTERSECTION NAVIGATION
======================================================================
Scenario: scenario_1 — Two vehicles perpendicular approach

[VALIDATION] t=0.5s V1 received PRIORITY_ASSIGNMENT priority=1 -> can_cross=True
[VALIDATION] t=0.5s V2 received PRIORITY_ASSIGNMENT priority=0 -> can_cross=False

--- PHASE 1 VALIDATION (C1: RSU delivery / C6: per-recipient reads) ---
  [PASS] RSU inbox contains only RSU-addressed mail: 1980 messages, 0 foreign
  [PASS] No cross-recipient (misrouted) vehicle deliveries: engine=0, v2i=0, v2v=0
  [PASS] Priority decisions reach vehicles: sent=400, delivered=392
----------------------------------------------------------------------

SIMULATION COMPLETED SUCCESSFULLY
```

---

## Documentation

| Document | Description |
|---|---|
| [Architecture](docs/architecture.md) | Full system architecture and design decisions |
| [UML Diagrams](docs/uml_diagram.md) | Class diagrams for all modules (Mermaid) |
| [Sequence Diagrams](docs/sequence_diagram.md) | Message flow between components |
| [System Overview](docs/system_overview.md) | High-level description with tables |
| [Future Improvements](docs/future_improvements.md) | Roadmap for v2.0+ |
| [Installation Guide](INSTALL.md) | Step-by-step setup for simulation & RPi |

---

## Team

| Roll No. | Name |
|---|---|
| 2300031089 | G. Hruday Bharadwaj |
| 2300030999 | K. S. Shanmukha Vijay |
| 2300030654 | S. Sai Datta Kiran |
| 2300032250 | I. Sarath Chandra |
| 2300033464 | K. Akshay |
| 2300069002 | M. Prashanth |

**Supervisor:** Dr. Pandian, Professor, Department of EEE  
**Institution:** Koneru Lakshmaiah Education Foundation (KLEF), Vijayawada  
**Program:** B.Tech — Electrical and Electronics Engineering, 2025–2026

---

## References

1. Chen, L., Li, X., & Sun, D. (2019). V2V-Based Cooperative Intersection Collision Avoidance System. *IEEE Trans. Intelligent Transportation Systems*, 20(7), 2673–2685.
2. Li, Y., Wang, J., & Zhang, H. (2020). Reinforcement Learning for Autonomous Intersection Management. *IEEE Access*, 8, 156789–156799.
3. Sommer, C., Tonguz, O. K., & Dressler, F. (2011). Traffic Information Systems. *IEEE Communications Magazine*, 49(11), 173–179.
4. Dresner, K., & Stone, P. (2008). A Multiagent Approach to Autonomous Intersection Management. *JAIR*, 31, 591–656.
5. IEEE Standard 802.11p — Wireless Access in Vehicular Environments (WAVE), 2010.

---

## License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for full text.

---

<div align="center">
Made with Python &nbsp;|&nbsp; Raspberry Pi 5 &nbsp;|&nbsp; KL Deemed University &nbsp;|&nbsp; 2025–2026
</div>
=======
# AI-Based-V2V-Intersection-Navigation-System
>>>>>>> ebf2848db219fe42713dde21aa3753b86439530d
