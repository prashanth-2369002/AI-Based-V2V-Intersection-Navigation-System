# System Architecture

## 1. High-Level Overview

The system is composed of three logical tiers:

```
┌──────────────────────────────────────────────┐
│  TIER 1: Vehicle On-Board Units (OBUs)        │
│  - Raspberry Pi 5 per vehicle                 │
│  - HC-SR04 ultrasonic sensor                  │
│  - L298N motor driver + 4× TT motors          │
│  - OLED SSD1306 display                       │
│  - Wi-Fi (V2V peer broadcast + V2I uplink)    │
└──────────────────┬───────────────────────────┘
                   │ V2V (peer-to-peer)
                   │ V2I (vehicle → RSU)
                   ▼
┌──────────────────────────────────────────────┐
│  TIER 2: Road-Side Unit (RSU)                 │
│  - Raspberry Pi 5                             │
│  - FCFS scheduler with timestamp validation   │
│  - AI trajectory predictor                   │
│  - Collision risk analyzer                   │
│  - Priority dispatcher (V2I downlink)         │
└──────────────────┬───────────────────────────┘
                   │ Priority assignment messages
                   ▼
┌──────────────────────────────────────────────┐
│  TIER 3: Vehicles receive decisions           │
│  - can_cross = True  → accelerate, cross      │
│  - can_cross = False → decelerate, hold       │
└──────────────────────────────────────────────┘
```

---

## 2. Module Architecture

### 2.1 `config.py` — Central Configuration

All tunable parameters live here. No magic numbers in business logic.

| Parameter | Default | Description |
|---|---|---|
| `GRID_SIZE` | 1000 px | Simulation world size |
| `V2V_RANGE` | 300 m | Vehicle-to-vehicle communication radius |
| `V2I_RANGE` | 500 m | RSU communication radius |
| `COMMUNICATION_DELAY_MS` | 50 ms | Simulated wireless latency |
| `MESSAGE_LOSS_RATE` | 2 % | Simulated packet drop probability |
| `COLLISION_THRESHOLD` | 30 px | Minimum safe inter-vehicle distance |
| `PREDICTION_WINDOW` | 10 steps | Look-ahead for trajectory prediction |
| `SIMULATION_TIME_STEPS` | 1000 | Total simulation steps |

### 2.2 `vehicle.py` — On-Board Unit Model

Each `Vehicle` object represents a single EV with an OBU. It manages:

- **State machine**: `APPROACHING → WAITING → CROSSING → COMPLETED`
- **Velocity control**: responds to collision risk and priority assignment
- **Position update**: Euler integration with configurable time step
- **Trajectory logging**: every position recorded for post-analysis
- **Message reception**: processes priority assignments and V2V peer data

**State Transition Rules:**

```
APPROACHING:
  distance < INTERSECTION_SIZE * 1.2 AND can_cross  → CROSSING
  distance < INTERSECTION_SIZE * 1.2 AND NOT cross  → WAITING

WAITING:
  can_cross becomes True                             → CROSSING
  distance < INTERSECTION_SIZE * 0.8 (safety)       → CROSSING

CROSSING:
  traveled > 80% of expected journey length          → COMPLETED
  distance_to_intersection > INTERSECTION_SIZE * 2   → COMPLETED
```

### 2.3 `rsu.py` — Road-Side Unit

Stateful coordinator that maintains a vehicle registry and enforces FCFS:

1. Receives vehicle registrations via `register_vehicle()`
2. Updates vehicle telemetry each step via `update_vehicle_info()`
3. Every 5 steps, calls `make_priority_decision()` which sorts by arrival timestamp
4. Vehicle with earliest arrival and lowest index is assigned `priority = 1` (cross)
5. All others receive `priority = 0` (wait)
6. Tracks collision detections via `detect_collision_risk()`

### 2.4 `fcfs.py` — Standalone FCFS Scheduler

Extracted, independently testable FCFS scheduler. Decoupled from RSU networking concerns. Used for:

- Unit testing the scheduling logic in isolation
- Benchmarking scheduling throughput
- Integration into alternative coordinator implementations

### 2.5 `communication.py` — Wireless Channel Simulation

Three classes:

| Class | Role |
|---|---|
| `CommunicationChannel` | Physical layer: range check, packet loss, propagation delay |
| `V2VCommunication` | Peer broadcast with per-receiver mailboxes |
| `V2ICommunication` | Uplink (vehicle→RSU) and downlink (RSU→vehicle) |

**Key design invariant**: `get_messages_for(receiver_id)` only dequeues messages addressed to that specific receiver. No message can be consumed by the wrong party.

### 2.6 `ai_predictor.py` — Trajectory Prediction + Collision Risk

**`TrajectoryPredictor`**:
- Maintains rolling position and velocity history per vehicle
- Applies exponential smoothing (`α = 0.8`) to velocity time series
- Projects forward `N` steps using current direction and smoothed velocity
- Computes min distance between predicted trajectories as collision risk

**Risk Score Formula:**
```
if min_predicted_distance < COLLISION_THRESHOLD:
    risk = 1.0 - (min_distance / COLLISION_THRESHOLD)
    if trajectories_converging:
        risk = min(1.0, risk * 1.2)
else:
    risk = 0.0
```

**`CollisionAnalyzer`**: wraps predictor, adds head-on detection and time-to-collision estimation.

### 2.7 `simulation.py` — Simulation Engine

10-step pipeline executed every time step:

```
Step 1  Update vehicle positions (velocity + collision risk input)
Step 2  Update trajectory history in AI predictor
Step 3A V2V broadcast — vehicles send to all peers
Step 3B V2V receive  — vehicles dequeue peer messages
Step 4  V2I uplink   — vehicles send telemetry to RSU
Step 5  RSU receive  — RSU dequeues vehicle messages
Step 6  RSU decide   — FCFS priority assignment (every 5 steps)
Step 7  V2I downlink — vehicles receive priority messages from RSU
Step 8  Collision detection — RSU scans all vehicle pairs
Step 9  Completion check — remove finished vehicles from RSU
Step 10 Record metrics
```

### 2.8 `hardware_interface.py` — Physical Hardware Abstraction

Abstracts Raspberry Pi GPIO operations behind clean interfaces:

| Class | Hardware |
|---|---|
| `UltrasonicSensor` | HC-SR04 via GPIO 23/24 |
| `MotorController` | L298N via GPIO 17/27/22/10 + PWM |
| `OLEDDisplay` | SSD1306 via I²C (smbus2 / luma.oled) |
| `HardwareInterface` | Composite: sensor + motor + display |

Graceful stub mode when running without GPIO (e.g., on Windows/macOS for development).

### 2.9 `evaluation.py` — Performance Metrics

Computes:
- **Priority Accuracy**: fraction of decisions where highest-priority vehicle crossed first
- **Collision Rate**: collisions per 100 vehicle-pairs
- **Communication Loss Rate**: packets dropped / packets sent
- **Average Latency**: mean message delivery delay
- **Throughput**: vehicles crossed per second of simulation time
- **RMSE**: trajectory prediction error vs actual path
- **F1 Score**: precision × recall balance for collision detection

### 2.10 `dataset_generator.py` — Synthetic Dataset

Generates labeled CSV rows:

```
vehicle_id, position_x, position_y, velocity, direction_x, direction_y,
eta_to_intersection, arrival_time, priority_assigned, collision_risk_score,
vehicle_type, scenario_id
```

Used for training ML models and offline benchmarking.

---

## 3. Communication Protocol

### Message Types

| Type | Sender | Receiver | Frequency |
|---|---|---|---|
| `VEHICLE_INFO` | Vehicle | All peers (V2V) | Every step |
| `VEHICLE_INFO` | Vehicle | RSU (V2I uplink) | Every step |
| `PRIORITY_ASSIGNMENT` | RSU | Vehicle (V2I downlink) | Every 5 steps |
| `COLLISION_WARNING` | RSU | Vehicle | On risk > 0.5 |
| `ACK` | Any | Any | On request |

### FCFS Decision Table (example)

| Vehicle ID | Timestamp Received | ETA (s) | Assigned Priority | Action |
|---|---|---|---|---|
| V1 | 12:00:05.235 | 8 | 1 | Proceed |
| V2 | 12:00:05.300 | 9 | 0 | Wait |

---

## 4. Simulation World

```
(0,0)                          (1000,0)
  ┌────────────────────────────────┐
  │       ↑ V3 spawn (500, 50)     │
  │                                │
  │ V1 →  ┌──────────┐  ← V2      │
  │(50,500)│Intersect.│(950,500)   │
  │       └──────────┘             │
  │              ↑                 │
  │       V4 spawn (500, 950)      │
  └────────────────────────────────┘
(0,1000)                       (1000,1000)

RSU at center: (500, 500)
Intersection box: 100×100 px centred at (500,500)
```

---

## 5. Design Decisions

| Decision | Rationale |
|---|---|
| Per-receiver mailboxes in channel | Prevents one vehicle consuming another's messages |
| FCFS every 5 steps (not every step) | Reduces RSU compute load; 5 × 0.1 s = 0.5 s decision cycle |
| Exponential smoothing α = 0.8 | Weights recent velocity heavily; responsive to sudden braking |
| Collision threshold 30 px | Calibrated to vehicle size (20 px) plus reaction distance |
| Euler integration | Sufficient accuracy at 0.1 s timestep; no iterative solver needed |
| Stub GPIO | Enables full simulation on any OS without hardware dependencies |
