# Sequence Diagrams

All diagrams use [Mermaid](https://mermaid.js.org/) syntax — rendered automatically on GitHub.

---

## 1. Vehicle Registration and Initial Approach

```mermaid
sequenceDiagram
    participant V1 as Vehicle V1 (OBU)
    participant V2 as Vehicle V2 (OBU)
    participant V2V as V2V Channel
    participant V2I as V2I Channel
    participant RSU as Road-Side Unit

    Note over V1,RSU: Both vehicles enter communication range

    V1->>V2I: send_vehicle_info_to_rsu(position, velocity, ETA)
    V2->>V2I: send_vehicle_info_to_rsu(position, velocity, ETA)

    V2I-->>RSU: deliver VEHICLE_INFO [V1] (t = arrival_time_V1)
    V2I-->>RSU: deliver VEHICLE_INFO [V2] (t = arrival_time_V2)

    RSU->>RSU: register_vehicle(V1)
    RSU->>RSU: register_vehicle(V2)

    Note over V1,V2: Peer-to-peer awareness via V2V

    V1->>V2V: broadcast_vehicle_info(V1_data)
    V2V-->>V2: deliver VEHICLE_INFO from V1

    V2->>V2V: broadcast_vehicle_info(V2_data)
    V2V-->>V1: deliver VEHICLE_INFO from V2
```

---

## 2. FCFS Priority Decision and Assignment

```mermaid
sequenceDiagram
    participant V1 as Vehicle V1
    participant V2 as Vehicle V2
    participant RSU as Road-Side Unit (RSU)
    participant FCFS as FCFS Scheduler
    participant AI as AI Predictor

    Note over RSU: Every 5 simulation steps

    RSU->>FCFS: make_priority_decision(current_time)
    FCFS->>FCFS: sort vehicles by arrival_time
    FCFS->>FCFS: V1.arrival_time < V2.arrival_time
    FCFS-->>RSU: {V1: priority=1, V2: priority=0}

    RSU->>AI: predict_trajectory(V1, V2)
    AI->>AI: calculate_collision_risk()
    AI-->>RSU: risk_score = 0.0

    RSU->>V1: send PRIORITY_ASSIGNMENT (priority=1, can_cross=True)
    RSU->>V2: send PRIORITY_ASSIGNMENT (priority=0, can_cross=False)

    Note over V1: Accelerates toward intersection
    Note over V2: Decelerates, holds position
```

---

## 3. Collision Risk Detection and Avoidance

```mermaid
sequenceDiagram
    participant V1 as Vehicle V1
    participant V2 as Vehicle V2
    participant RSU as RSU
    participant AI as AI Predictor

    Note over V1,V2: Near-simultaneous arrival detected

    RSU->>AI: analyze_vehicle_pair(V1_info, V2_info, t)
    AI->>AI: predict_trajectory(V1, steps=10)
    AI->>AI: predict_trajectory(V2, steps=10)
    AI->>AI: min_distance = min(distances between predicted paths)
    AI->>AI: risk_score = 1 - (min_distance / COLLISION_THRESHOLD)

    alt risk_score > 0.7 (HIGH RISK)
        AI-->>RSU: risk_score = 0.85
        RSU->>V1: send COLLISION_WARNING
        RSU->>V2: send COLLISION_WARNING
        Note over V1: Emergency deceleration (3× normal rate)
        Note over V2: Emergency deceleration (3× normal rate)

    else risk_score > 0.4 (MEDIUM RISK)
        AI-->>RSU: risk_score = 0.55
        Note over V1: Moderate deceleration (1.5× normal)
        Note over V2: Maintain safe spacing

    else risk_score <= 0.4 (LOW RISK)
        AI-->>RSU: risk_score = 0.10
        Note over V1: Normal crossing proceeds
    end
```

---

## 4. Complete Intersection Crossing Sequence

```mermaid
sequenceDiagram
    participant V1 as Vehicle V1 (Priority 1)
    participant V2 as Vehicle V2 (Priority 0)
    participant RSU as RSU
    participant HW as Hardware (Motor/Display)

    Note over V1,HW: Step 0 — Initialization

    RSU-->>V1: PRIORITY_ASSIGNMENT priority=1
    RSU-->>V2: PRIORITY_ASSIGNMENT priority=0

    V1->>HW: motor.forward(speed=30)
    V1->>HW: display.show_status(distance, APPROACHING, 1)
    V2->>HW: motor.set_speed(left=5, right=5)
    V2->>HW: display.show_status(distance, WAITING, 0)

    Note over V1: state → CROSSING

    loop V1 crossing intersection
        V1->>RSU: VEHICLE_INFO (position, velocity)
        RSU->>RSU: detect_collision_risk([V1, V2])
        V2->>RSU: VEHICLE_INFO (position, velocity)
    end

    Note over V1: Crossing complete → state = COMPLETED
    RSU->>RSU: remove_completed_vehicle(V1)

    RSU->>FCFS: re-evaluate queue
    RSU-->>V2: PRIORITY_ASSIGNMENT priority=1
    Note over V2: can_cross = True → state → CROSSING

    V2->>HW: motor.forward(speed=25)
    V2->>HW: display.show_status(distance, CROSSING, 1)

    Note over V2: Crossing complete → state = COMPLETED
```

---

## 5. Hardware Sensor → Motor Control Loop (Raspberry Pi)

```mermaid
sequenceDiagram
    participant US as HC-SR04 Sensor
    participant HW as HardwareInterface
    participant OLED as OLED Display
    participant MC as L298N Motor Controller
    participant NET as Network (V2I)
    participant RSU as RSU

    loop Every 0.1 s
        HW->>US: measure_distance()
        US-->>HW: distance_cm = 45.3

        HW->>NET: send_vehicle_info_to_rsu(position, velocity, ETA)
        NET-->>RSU: VEHICLE_INFO delivered

        RSU-->>NET: PRIORITY_ASSIGNMENT priority=1
        NET-->>HW: priority received

        alt distance_cm < 20 (obstacle detected)
            HW->>MC: stop()
            HW->>OLED: show_text(["OBSTACLE", "STOPPED"])
        else priority == 1 (cross)
            HW->>MC: forward(speed=50)
            HW->>OLED: show_status(distance_cm, CROSSING, 1)
        else priority == 0 (wait)
            HW->>MC: set_speed(5, 5)
            HW->>OLED: show_status(distance_cm, WAITING, 0)
        end
    end
```

---

## 6. Simulation Engine Step Pipeline

```mermaid
sequenceDiagram
    participant SIM as SimulationEngine
    participant V as Vehicles [V1..Vn]
    participant V2V as V2V Channel
    participant V2I as V2I Channel
    participant RSU as RSU
    participant AI as AI Predictor

    Note over SIM: step() called each time step

    SIM->>AI: calculate_collision_risk per vehicle pair
    AI-->>SIM: risk scores

    SIM->>V: update(current_time, collision_risk)
    SIM->>AI: update_vehicle_history(position, velocity)

    SIM->>V: get_vehicle_info() for V2V broadcast
    V-->>V2V: broadcast_vehicle_info()
    V2V-->>V: deliver peer messages

    SIM->>V: get_vehicle_info() for V2I uplink
    V-->>V2I: send_vehicle_info_to_rsu()
    V2I-->>RSU: deliver VEHICLE_INFO

    alt step_count % 5 == 0
        RSU->>RSU: make_priority_decision()
        RSU-->>V2I: send_priority_decision per vehicle
        V2I-->>V: deliver PRIORITY_ASSIGNMENT
    end

    SIM->>RSU: detect_collision_risk(all vehicles)
    RSU-->>SIM: collision_risks list

    SIM->>SIM: record_step_metrics()
    SIM->>SIM: step_count += 1
```
