# UML Class Diagrams

All diagrams use [Mermaid](https://mermaid.js.org/) syntax — rendered automatically on GitHub.

---

## 1. Core Domain Classes

```mermaid
classDiagram
    class Vehicle {
        +String vehicle_id
        +Tuple start_position
        +Tuple target_position
        +float speed
        +String vehicle_type
        +Tuple position
        +float current_velocity
        +VehicleState state
        +bool can_cross
        +int priority
        +List trajectory
        +List velocity_history
        +update(current_time, collision_risk)
        +receive_message(message, current_time)
        +get_status(current_time) VehicleStatus
        +get_vehicle_info(current_time) Dict
        +get_trajectory_data() Dict
        -_update_position(direction, current_time)
        -_update_state(current_time)
        -_distance_to_intersection() float
        -_calculate_eta() float
    }

    class VehicleState {
        <<enumeration>>
        IDLE
        APPROACHING
        WAITING
        CROSSING
        COMPLETED
    }

    class VehicleStatus {
        +String vehicle_id
        +Tuple position
        +float velocity
        +Tuple direction
        +float eta_to_intersection
        +VehicleState state
        +float timestamp
    }

    Vehicle --> VehicleState : has state
    Vehicle --> VehicleStatus : produces
```

---

## 2. RSU and FCFS Classes

```mermaid
classDiagram
    class RSU {
        +String rsu_id
        +Tuple position
        +RSUState state
        +Dict vehicle_registry
        +List priority_queue
        +List decisions_made
        +register_vehicle(vehicle_info, current_time)
        +update_vehicle_info(vehicle_info, current_time)
        +make_priority_decision(current_time) Dict
        +detect_collision_risk(vehicles) List
        +get_vehicle_priority(vehicle_id) int
        +remove_completed_vehicle(vehicle_id)
        +get_statistics() Dict
        -_calculate_distance(pos1, pos2) float
    }

    class RSUState {
        <<enumeration>>
        IDLE
        PROCESSING
        DECISION_MADE
    }

    class VehicleEntry {
        +String vehicle_id
        +float arrival_time
        +Tuple position
        +float velocity
        +String vehicle_type
        +float eta_to_intersection
        +int priority_level
        +bool processed
    }

    class FCFSScheduler {
        +List~VehicleEntry~ queue
        +List crossing_now
        +int max_concurrent
        +add_vehicle(vehicle_id, arrival_time, eta, vehicle_type) VehicleEntry
        +assign_priorities(current_time) Dict
        +complete_vehicle(vehicle_id)
        +get_queue_snapshot() List
        +get_statistics() Dict
        -_emergency_boost(entry) int
    }

    RSU --> RSUState : has state
    RSU --> VehicleEntry : manages
    RSU --> FCFSScheduler : uses
```

---

## 3. Communication Layer

```mermaid
classDiagram
    class Message {
        +String sender_id
        +String receiver_id
        +MessageType message_type
        +float timestamp
        +Dict payload
        +int sequence_number
        +int priority
        +to_dict() Dict
    }

    class MessageType {
        <<enumeration>>
        VEHICLE_INFO
        PRIORITY_ASSIGNMENT
        COLLISION_WARNING
        TRAJECTORY_CORRECTION
        ACK
    }

    class CommunicationChannel {
        +String name
        +float range_meters
        +float delay_ms
        +List message_queue
        +List sent_messages
        +List received_messages
        +int misrouted_deliveries
        +send_message(message, current_time, distance) bool
        +get_messages_for(receiver_id, current_time) List
        +get_statistics() Dict
    }

    class V2VCommunication {
        +CommunicationChannel channel
        +Dict vehicle_registry
        +register_vehicle(vehicle_id, position)
        +broadcast_vehicle_info(vehicle_id, vehicle_data, current_time) Dict
        +get_received_messages(vehicle_id, current_time) List
        +get_statistics() Dict
    }

    class V2ICommunication {
        +Tuple rsu_position
        +CommunicationChannel channel
        +Dict vehicle_registry
        +register_vehicle(vehicle_id)
        +send_vehicle_info_to_rsu(vehicle_id, vehicle_data, current_time) bool
        +get_rsu_messages(current_time) List
        +get_vehicle_messages(vehicle_id, current_time) List
        +send_priority_decision(vehicle_id, priority_level, current_time) bool
        +get_statistics() Dict
    }

    Message --> MessageType : has type
    V2VCommunication --> CommunicationChannel : owns
    V2ICommunication --> CommunicationChannel : owns
    CommunicationChannel --> Message : queues
```

---

## 4. AI Prediction Layer

```mermaid
classDiagram
    class TrajectoryPredictor {
        +Dict trajectory_history
        +Dict velocity_history
        +Dict predictions
        +update_vehicle_history(vehicle_id, position, velocity)
        +predict_trajectory(vehicle_id, current_position, velocity, direction, steps_ahead) List
        +calculate_collision_risk(vehicle_a, vehicle_b, prediction_window) float
        +detect_head_on_collision(vehicle_a, vehicle_b) bool
        +estimate_crossing_time(vehicle_data) float
        +calculate_trajectory_divergence(traj_a, traj_b) float
        +get_statistics() Dict
        -_exponential_smooth(values, alpha) float
        -_euclidean_distance(pos1, pos2) float
        -_distance_to_intersection(position) float
    }

    class CollisionAnalyzer {
        +TrajectoryPredictor predictor
        +List collision_events
        +Dict risk_history
        +analyze_vehicle_pair(vehicle_a, vehicle_b, current_time) Dict
        +get_collision_summary() Dict
        -_estimate_time_to_collision(vehicle_a, vehicle_b) float
    }

    CollisionAnalyzer --> TrajectoryPredictor : owns
```

---

## 5. Simulation Engine

```mermaid
classDiagram
    class SimulationEngine {
        +String scenario_name
        +Dict scenario_config
        +Dict vehicles
        +RSU rsu
        +V2VCommunication v2v_communication
        +V2ICommunication v2i_communication
        +TrajectoryPredictor trajectory_predictor
        +CollisionAnalyzer collision_analyzer
        +float current_time
        +int step_count
        +Dict performance_metrics
        +initialize_scenario()
        +step() bool
        +run_simulation() Dict
        +get_results() Dict
        +save_results(output_dir) str
        -_calculate_vehicle_collision_risk(vehicle) float
        -_record_step_metrics()
        -_print_validation_summary()
        -_make_serializable(obj)
    }

    SimulationEngine --> Vehicle : manages
    SimulationEngine --> RSU : owns
    SimulationEngine --> V2VCommunication : owns
    SimulationEngine --> V2ICommunication : owns
    SimulationEngine --> TrajectoryPredictor : owns
    SimulationEngine --> CollisionAnalyzer : owns
```

---

## 6. Hardware Interface

```mermaid
classDiagram
    class UltrasonicSensor {
        +int trig_pin
        +int echo_pin
        +bool gpio_available
        +measure_distance() float
        +is_obstacle_detected(threshold_cm) bool
        +cleanup()
    }

    class MotorController {
        +int in1_pin
        +int in2_pin
        +int in3_pin
        +int in4_pin
        +int ena_pin
        +int enb_pin
        +bool gpio_available
        +forward(speed)
        +backward(speed)
        +turn_left(speed)
        +turn_right(speed)
        +stop()
        +set_speed(left_speed, right_speed)
        +cleanup()
    }

    class OLEDDisplay {
        +int i2c_address
        +bool display_available
        +show_text(lines)
        +show_status(distance, state, priority)
        +clear()
        +cleanup()
    }

    class HardwareInterface {
        +UltrasonicSensor sensor
        +MotorController motor
        +OLEDDisplay display
        +String vehicle_id
        +bool running
        +start()
        +stop()
        +run_live_mode()
        +update_display(distance, state, priority)
        +execute_movement(priority, distance)
        +cleanup()
    }

    HardwareInterface --> UltrasonicSensor : owns
    HardwareInterface --> MotorController : owns
    HardwareInterface --> OLEDDisplay : owns
```

---

## 7. Evaluation Module

```mermaid
classDiagram
    class EvaluationMetrics {
        +Dict results
        +float priority_accuracy
        +float collision_rate
        +float comm_loss_rate
        +float avg_latency_ms
        +float throughput
        +float rmse
        +float precision
        +float recall
        +float f1_score
        +compute_all() Dict
        +compute_priority_accuracy() float
        +compute_collision_rate() float
        +compute_communication_metrics() Dict
        +compute_trajectory_rmse() float
        +compute_classification_metrics() Dict
        +print_report()
        +export_csv(filepath)
    }
```
