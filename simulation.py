"""
Main simulation engine for V2V Negotiation System
Orchestrates vehicles, RSU, communication, and AI prediction
"""

import json
import os
from typing import Dict
from datetime import datetime

import config
from vehicle import Vehicle, VehicleState
from rsu import RSU
from communication import V2VCommunication, V2ICommunication
from ai_predictor import TrajectoryPredictor, CollisionAnalyzer


class SimulationEngine:
    """Main simulation orchestrator"""

    def __init__(self, scenario: str = 'scenario_1'):
        self.scenario_name = scenario
        self.scenario_config = config.SCENARIOS.get(scenario, config.SCENARIOS['scenario_1'])

        # Initialize components
        self.vehicles: Dict[str, Vehicle] = {}
        self.rsu = RSU()

        self.v2v_communication = V2VCommunication()
        self.v2i_communication = V2ICommunication(config.RSU_POSITION)

        self.trajectory_predictor = TrajectoryPredictor()
        self.collision_analyzer = CollisionAnalyzer()

        # Simulation state
        self.current_time = 0.0
        self.step_count = 0
        self.simulation_log = []
        self.performance_metrics = {
            'total_collisions_avoided': 0,
            'successful_crossings': 0,
            'total_wait_time': 0,
            'communication_delays': [],
        }

        # Phase 1 (C1/C6) delivery validation counters
        self.validation = {
            'priority_decisions_sent': 0,
            'priority_msgs_delivered': {},   # vehicle_id -> count
            'rsu_inbox_total': 0,
            'rsu_inbox_foreign': 0,          # non-RSU mail seen by RSU (must stay 0)
            'vehicle_inbox_misrouted': 0,    # mail for A handed to B (must stay 0)
            'last_logged_priority': {},      # vehicle_id -> last priority we logged
        }

    def initialize_scenario(self) -> None:
        """Initialize vehicles for the current scenario"""
        scenario = self.scenario_config
        num_vehicles = scenario.get('vehicles', 2)
        speeds = scenario.get('vehicle_speeds', [25] * num_vehicles)
        arrival_times = scenario.get('arrival_times', list(range(num_vehicles)))
        vehicle_types = scenario.get('vehicle_types', ['regular'] * num_vehicles)

        for i in range(num_vehicles):
            vehicle_id = f"V{i+1}"

            # Determine spawn point and target (cycling through spawn points)
            spawn_point = config.SPAWN_POINTS[i % len(config.SPAWN_POINTS)]
            target_point = (
                config.INTERSECTION_CENTER[0] + (spawn_point[0] - config.INTERSECTION_CENTER[0]) * 2,
                config.INTERSECTION_CENTER[1] + (spawn_point[1] - config.INTERSECTION_CENTER[1]) * 2,
            )

            vehicle = Vehicle(
                vehicle_id=vehicle_id,
                start_position=spawn_point,
                target_position=target_point,
                speed=speeds[i],
                vehicle_type=vehicle_types[i]
            )

            # Delay vehicle arrival if specified
            if arrival_times[i] > 0:
                offset = arrival_times[i] * 20  # Convert to pixel distance
                spawn_adjusted = (
                    spawn_point[0] - (spawn_point[0] - config.INTERSECTION_CENTER[0]) / 100 * offset,
                    spawn_point[1] - (spawn_point[1] - config.INTERSECTION_CENTER[1]) / 100 * offset,
                )
                vehicle.position = spawn_adjusted
                vehicle.trajectory = [spawn_adjusted]

            self.vehicles[vehicle_id] = vehicle

            # Register with RSU and communication
            self.rsu.register_vehicle(vehicle.get_vehicle_info(0), 0)
            self.v2v_communication.register_vehicle(vehicle_id, vehicle.position)
            self.v2i_communication.register_vehicle(vehicle_id)

    def step(self) -> bool:
        """Execute one simulation step"""
        self.current_time = self.step_count * config.TIME_STEP_DURATION

        if self.step_count >= config.SIMULATION_TIME_STEPS:
            return False

        # Step 1: Update vehicle positions
        for vehicle in self.vehicles.values():
            collision_risk = self._calculate_vehicle_collision_risk(vehicle)
            vehicle.update(self.current_time, collision_risk)

        # Step 2: Update trajectory history
        for vehicle in self.vehicles.values():
            vehicle_info = vehicle.get_vehicle_info(self.current_time)
            self.trajectory_predictor.update_vehicle_history(
                vehicle.vehicle_id,
                vehicle.position,
                vehicle.current_velocity
            )

        # Step 3A: V2V Communication - vehicles broadcast to each other
        # First update V2V registry with current positions
        for vehicle in self.vehicles.values():
            if vehicle.vehicle_id in self.v2v_communication.vehicle_registry:
                self.v2v_communication.vehicle_registry[vehicle.vehicle_id]['last_position'] = vehicle.position

        for vehicle in self.vehicles.values():
            if vehicle.state != VehicleState.COMPLETED:
                vehicle_info = vehicle.get_vehicle_info(self.current_time)
                self.v2v_communication.broadcast_vehicle_info(
                    vehicle.vehicle_id,
                    vehicle_info,
                    self.current_time
                )

        # Step 3B: Vehicles receive V2V messages from other vehicles
        for vehicle in self.vehicles.values():
            v2v_messages = self.v2v_communication.get_received_messages(
                vehicle.vehicle_id,
                self.current_time
            )
            for msg in v2v_messages:
                vehicle.receive_message({
                    'type': 'v2v_info',
                    'sender': msg.sender_id,
                    'data': msg.payload
                }, self.current_time)

        # Step 4: V2I Communication - vehicles send info to RSU
        for vehicle in self.vehicles.values():
            if vehicle.state != VehicleState.COMPLETED:
                vehicle_info = vehicle.get_vehicle_info(self.current_time)
                self.v2i_communication.send_vehicle_info_to_rsu(
                    vehicle.vehicle_id,
                    vehicle_info,
                    self.current_time
                )

        # Step 5: RSU receives messages and processes
        rsu_messages = self.v2i_communication.get_rsu_messages(self.current_time)
        for msg in rsu_messages:
            self.validation['rsu_inbox_total'] += 1
            if getattr(msg, 'receiver_id', "RSU") != "RSU":
                self.validation['rsu_inbox_foreign'] += 1
                print(f"[VALIDATION FAIL] t={self.current_time:.1f}s RSU dequeued "
                      f"mail addressed to {msg.receiver_id}")

            if hasattr(msg, 'payload'):
                vehicle_info = msg.payload
            else:
                vehicle_info = msg

            if isinstance(vehicle_info, dict) and 'vehicle_id' in vehicle_info:
                self.rsu.update_vehicle_info(vehicle_info, self.current_time)
                self.rsu.register_vehicle(vehicle_info, self.current_time)

        # Step 6: RSU makes priority decisions
        if self.step_count % 5 == 0:
            decisions = self.rsu.make_priority_decision(self.current_time)
            for vehicle_id, priority in decisions.items():
                if vehicle_id in self.vehicles:
                    sent = self.v2i_communication.send_priority_decision(
                        vehicle_id,
                        priority,
                        self.current_time
                    )
                    if sent:
                        self.validation['priority_decisions_sent'] += 1

        # Step 7: Vehicles receive V2I messages from RSU
        for vehicle_id, vehicle in self.vehicles.items():
            messages = self.v2i_communication.get_vehicle_messages(vehicle_id, self.current_time)
            for msg in messages:
                if getattr(msg, 'receiver_id', vehicle_id) != vehicle_id:
                    self.validation['vehicle_inbox_misrouted'] += 1
                    print(f"[VALIDATION FAIL] t={self.current_time:.1f}s mail for "
                          f"{msg.receiver_id} delivered to {vehicle_id}")

                if hasattr(msg, 'payload') and 'priority' in msg.payload:
                    self.validation['priority_msgs_delivered'][vehicle_id] = (
                        self.validation['priority_msgs_delivered'].get(vehicle_id, 0) + 1
                    )
                    vehicle.priority = msg.payload['priority']
                    vehicle.can_cross = (vehicle.priority == 1)
                    # Log only priority changes, not every periodic re-send
                    if self.validation['last_logged_priority'].get(vehicle_id) != vehicle.priority:
                        self.validation['last_logged_priority'][vehicle_id] = vehicle.priority
                        print(f"[VALIDATION] t={self.current_time:.1f}s {vehicle_id} received "
                              f"PRIORITY_ASSIGNMENT priority={vehicle.priority} "
                              f"-> can_cross={vehicle.can_cross}")
                vehicle.receive_message(msg.to_dict() if hasattr(msg, 'to_dict') else msg, self.current_time)

        # Step 8: Collision detection and analysis
        vehicle_list = [v.get_vehicle_info(self.current_time) for v in self.vehicles.values()]
        for i, v_a in enumerate(vehicle_list):
            for v_b in vehicle_list[i+1:]:
                collision_risks = self.rsu.detect_collision_risk([v_a, v_b])
                for risk in collision_risks:
                    if risk['risk_score'] > 0.5:
                        self.performance_metrics['total_collisions_avoided'] += 1

        # Step 9: Remove completed vehicles from RSU tracking
        for vehicle in self.vehicles.values():
            if vehicle.state == VehicleState.COMPLETED and vehicle.crossing_completed:
                self.rsu.remove_completed_vehicle(vehicle.vehicle_id)
                if vehicle.state == VehicleState.COMPLETED:
                    self.performance_metrics['successful_crossings'] += 1

        # Step 10: Record metrics
        self._record_step_metrics()

        self.step_count += 1
        return True

    def _calculate_vehicle_collision_risk(self, vehicle: Vehicle) -> float:
        """Calculate collision risk for a single vehicle from all others"""
        vehicle_info = vehicle.get_vehicle_info(self.current_time)
        max_risk = 0.0

        for other_vehicle in self.vehicles.values():
            if other_vehicle.vehicle_id == vehicle.vehicle_id:
                continue

            other_info = other_vehicle.get_vehicle_info(self.current_time)
            risk = self.collision_analyzer.predictor.calculate_collision_risk(
                vehicle_info,
                other_info
            )
            max_risk = max(max_risk, risk)

        return max_risk

    def _record_step_metrics(self) -> None:
        """Record simulation metrics for current step"""
        for vehicle in self.vehicles.values():
            if vehicle.state == VehicleState.COMPLETED and not vehicle.crossing_completed:
                vehicle.crossing_completed = True
                self.performance_metrics['successful_crossings'] += 1
            elif vehicle.state == VehicleState.WAITING:
                self.performance_metrics['total_wait_time'] += config.TIME_STEP_DURATION

    def run_simulation(self) -> Dict:
        """Run complete simulation"""
        self.initialize_scenario()

        print(f"Starting simulation: {self.scenario_name}")
        print(f"Vehicles: {len(self.vehicles)}")

        while self.step():
            if self.step_count % 100 == 0:
                print(f"Step {self.step_count}/{config.SIMULATION_TIME_STEPS}")

        print("Simulation completed!")
        self._print_validation_summary()
        return self.get_results()

    def _print_validation_summary(self) -> None:
        """Unit-style validation report for Phase 1 (C1/C6) message delivery"""
        v = self.validation
        v2i_stats = self.v2i_communication.get_statistics()
        v2v_stats = self.v2v_communication.get_statistics()
        delivered_total = sum(v['priority_msgs_delivered'].values())

        def check(label: str, ok: bool, detail: str) -> None:
            print(f"  [{'PASS' if ok else 'FAIL'}] {label}: {detail}")

        print("\n--- PHASE 1 VALIDATION (C1: RSU priority delivery / C6: per-recipient reads) ---")
        check("RSU inbox contains only RSU-addressed mail",
              v['rsu_inbox_foreign'] == 0,
              f"{v['rsu_inbox_total']} messages dequeued, {v['rsu_inbox_foreign']} foreign")
        check("No cross-recipient (misrouted) vehicle deliveries",
              v['vehicle_inbox_misrouted'] == 0 and v2i_stats['misrouted_deliveries'] == 0
              and v2v_stats['misrouted_deliveries'] == 0,
              f"engine={v['vehicle_inbox_misrouted']}, "
              f"v2i_channel={v2i_stats['misrouted_deliveries']}, "
              f"v2v_channel={v2v_stats['misrouted_deliveries']}")
        check("Priority decisions reach vehicles",
              delivered_total > 0 or v['priority_decisions_sent'] == 0,
              f"sent={v['priority_decisions_sent']}, delivered={delivered_total} "
              f"(per vehicle: {v['priority_msgs_delivered'] or '{}'}; "
              f"difference = simulated packet loss + in-flight at end)")
        print(f"  [INFO] V2I deliveries by receiver: {v2i_stats['delivered_by_receiver']}")
        print(f"  [INFO] V2V deliveries by receiver: {v2v_stats['delivered_by_receiver']}")
        print("--- END VALIDATION ---\n")

    def get_results(self) -> Dict:
        """Get simulation results"""
        vehicle_trajectories = {
            v_id: v.get_trajectory_data()
            for v_id, v in self.vehicles.items()
        }

        rsu_stats = self.rsu.get_statistics()
        v2v_stats = self.v2v_communication.get_statistics()
        v2i_stats = self.v2i_communication.get_statistics()

        collision_summary = self.collision_analyzer.get_collision_summary()

        results = {
            'scenario': self.scenario_name,
            'simulation_time': self.current_time,
            'total_steps': self.step_count,
            'vehicle_trajectories': vehicle_trajectories,
            'rsu_statistics': rsu_stats,
            'communication_statistics': {
                'v2v': v2v_stats,
                'v2i': v2i_stats,
            },
            'collision_analysis': collision_summary,
            'performance_metrics': self.performance_metrics,
        }

        return results

    def save_results(self, output_dir: str = config.DATA_OUTPUT_DIR) -> str:
        """Save simulation results to file"""
        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{output_dir}simulation_{self.scenario_name}_{timestamp}.json"

        results = self.get_results()

        with open(filename, 'w') as f:
            # Convert numpy types and handle non-serializable objects
            json_results = self._make_serializable(results)
            json.dump(json_results, f, indent=2)

        print(f"Results saved to: {filename}")
        return filename

    def _make_serializable(self, obj):
        """Convert objects to JSON-serializable format"""
        if isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._make_serializable(item) for item in obj]
        elif hasattr(obj, 'value'):  # Enum
            return obj.value
        elif isinstance(obj, float):
            if obj == float('inf'):
                return "Infinity"
            elif obj == float('-inf'):
                return "-Infinity"
            return obj
        else:
            return obj
