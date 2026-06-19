"""
Road Side Unit (RSU) module for intersection management
Implements FCFS priority assignment and coordination logic
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

import config


class RSUState(Enum):
    """States of the RSU"""
    IDLE = "idle"
    PROCESSING = "processing"
    DECISION_MADE = "decision_made"


@dataclass
class VehicleEntry:
    """Entry in RSU vehicle queue for FCFS"""
    vehicle_id: str
    arrival_time: float
    position: Tuple[float, float]
    velocity: float
    vehicle_type: str
    eta_to_intersection: float
    priority_level: int = -1
    processed: bool = False
    assigned_time: Optional[float] = None


class RSU:
    """Road Side Unit - manages intersection coordination"""

    def __init__(self, rsu_id: str = "RSU_1"):
        self.rsu_id = rsu_id
        self.position = config.RSU_POSITION
        self.state = RSUState.IDLE

        # Vehicle management
        self.vehicle_registry: Dict[str, VehicleEntry] = {}
        self.priority_queue: List[Tuple[float, str]] = []  # (arrival_time, vehicle_id)
        self.active_vehicles: Dict[str, VehicleEntry] = {}

        # Statistics
        self.decisions_made: List[Dict] = []
        self.collision_detections: List[Dict] = []
        self.processing_times: List[float] = []

        # Configuration
        self.max_vehicles_in_intersection = 1
        self.current_crossing_vehicles: List[str] = []

    def register_vehicle(self, vehicle_info: Dict, current_time: float) -> None:
        """Register a vehicle approaching the intersection"""
        vehicle_id = vehicle_info['vehicle_id']

        if vehicle_id not in self.vehicle_registry:
            entry = VehicleEntry(
                vehicle_id=vehicle_id,
                arrival_time=current_time,
                position=vehicle_info['position'],
                velocity=vehicle_info['velocity'],
                vehicle_type=vehicle_info.get('vehicle_type', 'regular'),
                eta_to_intersection=vehicle_info.get('eta_to_intersection', float('inf')),
            )
            self.vehicle_registry[vehicle_id] = entry
            self.active_vehicles[vehicle_id] = entry

    def update_vehicle_info(self, vehicle_info: Dict, current_time: float) -> None:
        """Update vehicle information from V2I messages"""
        vehicle_id = vehicle_info['vehicle_id']

        if vehicle_id in self.vehicle_registry:
            entry = self.vehicle_registry[vehicle_id]
            entry.position = vehicle_info['position']
            entry.velocity = vehicle_info['velocity']
            entry.eta_to_intersection = vehicle_info.get('eta_to_intersection', float('inf'))

    def make_priority_decision(self, current_time: float) -> Dict[str, int]:
        """
        Make priority assignment decisions using FCFS
        
        Returns:
            Dictionary mapping vehicle_id to priority level (1=cross, 0=wait)
        """
        decisions = {}

        # Get all unprocessed vehicles sorted by arrival time
        unprocessed = [
            (entry.arrival_time, vehicle_id)
            for vehicle_id, entry in self.active_vehicles.items()
            if not entry.processed and entry.eta_to_intersection < float('inf')
        ]

        unprocessed.sort()

        # Assign priorities based on FCFS
        vehicles_crossing_now = len([
            v_id for v_id in self.current_crossing_vehicles
            if v_id in self.active_vehicles
        ])

        for idx, (arrival_time, vehicle_id) in enumerate(unprocessed):
            entry = self.active_vehicles[vehicle_id]

            if idx == 0 and vehicles_crossing_now == 0:
                # First vehicle can cross
                priority_level = 1
                entry.priority_level = priority_level
                entry.processed = True
                self.current_crossing_vehicles.append(vehicle_id)
            else:
                # Other vehicles must wait
                priority_level = 0
                entry.priority_level = priority_level

            decisions[vehicle_id] = priority_level

            # Record decision
            self.decisions_made.append({
                'timestamp': current_time,
                'vehicle_id': vehicle_id,
                'priority': priority_level,
                'arrival_time': arrival_time,
            })

        self.state = RSUState.DECISION_MADE
        self.processing_times.append(config.RSU_DECISION_TIME)
        return decisions

    def detect_collision_risk(self, vehicles: List[Dict]) -> List[Dict]:
        """
        Detect potential collision risks
        
        Args:
            vehicles: List of vehicle status dictionaries
            
        Returns:
            List of collision risk entries
        """
        collision_risks = []

        for i, v1 in enumerate(vehicles):
            for v2 in vehicles[i+1:]:
                if v1['vehicle_id'] == v2['vehicle_id']:
                    continue

                # Calculate distance and check for collision risk
                distance = self._calculate_distance(v1['position'], v2['position'])
                relative_velocity = v1['velocity'] - v2['velocity']

                # Simple collision prediction
                if distance < config.COLLISION_THRESHOLD and relative_velocity > 0:
                    collision_risk_score = 1.0 - (distance / config.COLLISION_THRESHOLD)

                    risk_entry = {
                        'vehicle_1': v1['vehicle_id'],
                        'vehicle_2': v2['vehicle_id'],
                        'distance': distance,
                        'risk_score': collision_risk_score,
                    }
                    collision_risks.append(risk_entry)
                    self.collision_detections.append(risk_entry)

        return collision_risks

    def get_vehicle_priority(self, vehicle_id: str) -> int:
        """Get current priority level of a vehicle"""
        if vehicle_id in self.vehicle_registry:
            return self.vehicle_registry[vehicle_id].priority_level
        return -1

    def remove_completed_vehicle(self, vehicle_id: str) -> None:
        """Remove a vehicle that has completed crossing"""
        if vehicle_id in self.active_vehicles:
            del self.active_vehicles[vehicle_id]

        if vehicle_id in self.current_crossing_vehicles:
            self.current_crossing_vehicles.remove(vehicle_id)

    def _calculate_distance(self, pos1: Tuple[float, float],
                           pos2: Tuple[float, float]) -> float:
        """Calculate Euclidean distance between two positions"""
        return ((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)**0.5

    def get_statistics(self) -> Dict:
        """Get RSU statistics"""
        total_decisions = len(self.decisions_made)
        vehicles_crossed = sum(
            1 for entry in self.vehicle_registry.values()
            if entry.processed
        )

        avg_processing_time = (
            sum(self.processing_times) / len(self.processing_times)
            if self.processing_times else 0
        )

        return {
            'rsu_id': self.rsu_id,
            'total_vehicles_managed': len(self.vehicle_registry),
            'vehicles_crossed': vehicles_crossed,
            'total_decisions': total_decisions,
            'collision_detections': len(self.collision_detections),
            'avg_processing_time': avg_processing_time,
            'active_vehicles': len(self.active_vehicles),
        }

    def get_detailed_decisions(self) -> List[Dict]:
        """Get detailed decision history"""
        return self.decisions_made

    def get_collision_risk_summary(self) -> Dict:
        """Get collision risk detection summary"""
        if not self.collision_detections:
            return {
                'total_collision_events': 0,
                'average_collision_risk_score': 0,
                'max_risk_score': 0,
            }

        risk_scores = [event['risk_score'] for event in self.collision_detections]
        return {
            'total_collision_events': len(self.collision_detections),
            'average_collision_risk_score': sum(risk_scores) / len(risk_scores),
            'max_risk_score': max(risk_scores),
        }
