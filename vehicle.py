"""
Vehicle module for the V2V Negotiation System
Represents an intelligent vehicle with on-board unit capabilities
"""

import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

import config


class VehicleState(Enum):
    """States of a vehicle in the system"""
    IDLE = "idle"
    APPROACHING = "approaching"
    WAITING = "waiting"
    CROSSING = "crossing"
    COMPLETED = "completed"


@dataclass
class VehicleStatus:
    """Current status of a vehicle"""
    vehicle_id: str
    position: Tuple[float, float]
    velocity: float
    direction: Tuple[float, float]  # unit vector
    eta_to_intersection: float
    state: VehicleState
    timestamp: float


class Vehicle:
    """Represents an intelligent vehicle with V2V/V2I capabilities"""

    def __init__(self, vehicle_id: str, start_position: Tuple[float, float],
                 target_position: Tuple[float, float], speed: float,
                 vehicle_type: str = 'regular'):
        """
        Initialize a vehicle
        
        Args:
            vehicle_id: Unique identifier
            start_position: Starting position (x, y)
            target_position: Target position after intersection
            speed: Target speed (pixels/second)
            vehicle_type: 'regular', 'emergency', 'heavy'
        """
        self.vehicle_id = vehicle_id
        self.start_position = start_position
        self.target_position = target_position
        self.speed = speed
        self.vehicle_type = vehicle_type

        # State variables
        self.position: Tuple[float, float] = start_position
        self.current_velocity = 0.0
        self.state = VehicleState.APPROACHING
        self.distance_traveled = 0.0

        # Intersection crossing
        self.can_cross = False
        self.priority = None
        self.crossing_started = False
        self.crossing_completed = False

        # Communication
        self.last_v2v_update = 0.0
        self.last_v2i_update = 0.0
        self.received_messages: List[Dict] = []

        # Trajectory history for analysis
        self.trajectory: List[Tuple[float, float]] = [start_position]
        self.velocity_history: List[float] = [0.0]
        self.state_history: List[Tuple[float, VehicleState]] = [(0.0, VehicleState.APPROACHING)]

    def update(self, current_time: float, collision_risk: float = 0.0) -> None:
        """
        Update vehicle state and position
        
        Args:
            current_time: Current simulation time
            collision_risk: Predicted collision risk (0-1)
        """
        # Calculate direction to intersection
        direction = self._calculate_direction(self.position, config.INTERSECTION_CENTER)

        # Update velocity based on state and collision risk
        target_distance = self._distance_to_intersection()

        if self.state == VehicleState.APPROACHING:
            # HIGH PRIORITY COLLISION AVOIDANCE
            if collision_risk > 0.7:
                # Emergency deceleration for high collision risk
                decel_rate = config.VEHICLE_DECELERATION * 3.0
                self.current_velocity = max(0, self.current_velocity - decel_rate)
            elif collision_risk > 0.4:
                # Moderate deceleration for medium risk
                decel_rate = config.VEHICLE_DECELERATION * 1.5
                self.current_velocity = max(0, self.current_velocity - decel_rate)
            # If at intersection and has priority, aggressive acceleration
            elif self.can_cross and target_distance < 200:
                self.current_velocity = min(self.speed, self.current_velocity + 3.0)
            # If waiting for priority, decelerate to near stop
            elif self.priority == 0 and target_distance < 250:
                self.current_velocity = max(5, self.current_velocity - 2.0)  # Slow but not stopped
            # Normal approach - gentle acceleration
            else:
                self.current_velocity = min(self.speed, self.current_velocity + 1.0)

        elif self.state == VehicleState.WAITING:
            # If priority is granted, start accelerating to cross
            if self.can_cross:
                if collision_risk > 0.7:
                    self.current_velocity = max(0, self.current_velocity - config.VEHICLE_DECELERATION * 1.5)
                else:
                    # Accelerate to cross quickly
                    self.current_velocity = min(self.speed, self.current_velocity + 1.5)
            else:
                # No priority - maintain safe distance
                if collision_risk > 0.6:
                    self.current_velocity = 0
                else:
                    self.current_velocity = max(0, self.current_velocity - config.VEHICLE_DECELERATION * 2)

        elif self.state == VehicleState.CROSSING:
            # Move at target speed through intersection unless collision risk
            if collision_risk > 0.7:
                self.current_velocity = max(0, self.current_velocity - config.VEHICLE_DECELERATION * 2)
            else:
                self.current_velocity = self.speed

        # Update position
        self._update_position(direction, current_time)

        # Update state
        self._update_state(current_time)

        # Record history
        self.trajectory.append(self.position)
        self.velocity_history.append(self.current_velocity)

    def _update_position(self, direction: Tuple[float, float], current_time: float) -> None:
        """Update vehicle position based on current velocity and direction"""
        dx = direction[0] * self.current_velocity * config.TIME_STEP_DURATION
        dy = direction[1] * self.current_velocity * config.TIME_STEP_DURATION

        new_x = self.position[0] + dx
        new_y = self.position[1] + dy

        self.position = (new_x, new_y)
        self.distance_traveled += self.current_velocity * config.TIME_STEP_DURATION

    def _update_state(self, current_time: float) -> None:
        """Update vehicle state based on position and priorities"""
        distance_to_intersection = self._distance_to_intersection()
        
        # Crossing completion: check if vehicle has gone past the intersection
        # For spawn point at 50, intersection at 500, intersection is 450 pixels away
        # Once past 500, should continue for at least 100 pixels more (total 550+) before completion
        
        if self.state == VehicleState.APPROACHING:
            if distance_to_intersection < config.INTERSECTION_SIZE * 1.2:
                if self.can_cross:
                    self.state = VehicleState.CROSSING
                    self.crossing_started = True
                else:
                    self.state = VehicleState.WAITING
            
            self.state_history.append((current_time, self.state))

        elif self.state == VehicleState.CROSSING:
            # Vehicle has crossed if it's traveled significantly past the intersection
            # Using distance traveled instead of distance to intersection to handle all directions
            if self.crossing_started:
                # Calculate how far the vehicle has traveled from its start
                traveled = self._distance(self.position, self.start_position)
                # Target is to go ~450 pixels to reach intersection + 150 more to cross = 600 total
                expected_distance = self._distance(self.target_position, self.start_position)
                if traveled > expected_distance * 0.8:  # 80% of expected journey
                    self.state = VehicleState.COMPLETED
                    self.crossing_completed = True
                    self.state_history.append((current_time, self.state))
                # Alternative: if we're very far from intersection (passed it significantly)
                elif distance_to_intersection > config.INTERSECTION_SIZE * 2:
                    self.state = VehicleState.COMPLETED
                    self.crossing_completed = True
                    self.state_history.append((current_time, self.state))

        elif self.state == VehicleState.WAITING:
            # Check if priority changed and we can now cross
            if self.can_cross:
                self.state = VehicleState.CROSSING
                self.crossing_started = True
                self.state_history.append((current_time, self.state))
            # Or if we got too close, transition to crossing anyway for safety
            elif distance_to_intersection < config.INTERSECTION_SIZE * 0.8:
                self.state = VehicleState.CROSSING
                self.crossing_started = True
                self.state_history.append((current_time, self.state))

    def _distance_to_intersection(self) -> float:
        """Calculate distance from current position to intersection center"""
        return self._distance(self.position, config.INTERSECTION_CENTER)

    def _calculate_direction(self, from_pos: Tuple[float, float],
                            to_pos: Tuple[float, float]) -> Tuple[float, float]:
        """Calculate unit direction vector from one position to another"""
        dx = to_pos[0] - from_pos[0]
        dy = to_pos[1] - from_pos[1]
        distance = math.sqrt(dx**2 + dy**2)

        if distance == 0:
            return (0, 0)

        return (dx / distance, dy / distance)

    def _distance(self, pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
        """Calculate Euclidean distance between two positions"""
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

    def get_status(self, current_time: float) -> VehicleStatus:
        """Get current vehicle status"""
        direction = self._calculate_direction(self.position, config.INTERSECTION_CENTER)
        eta = self._calculate_eta()

        return VehicleStatus(
            vehicle_id=self.vehicle_id,
            position=self.position,
            velocity=self.current_velocity,
            direction=direction,
            eta_to_intersection=eta,
            state=self.state,
            timestamp=current_time
        )

    def _calculate_eta(self) -> float:
        """Calculate estimated time of arrival at intersection"""
        distance = self._distance_to_intersection()
        if self.current_velocity > 0:
            return distance / self.current_velocity
        return float('inf')

    def receive_message(self, message: Dict, current_time: float) -> None:
        """Receive a message from RSU or other vehicle"""
        message['received_at'] = current_time
        self.received_messages.append(message)

        # Process priority assignment
        if message.get('type') == 'priority_assignment':
            self.priority = message.get('priority')
            self.can_cross = (self.priority == 1)

    def get_vehicle_info(self, current_time: float) -> Dict:
        """Get vehicle information for V2V/V2I communication"""
        direction = self._calculate_direction(self.position, config.INTERSECTION_CENTER)

        return {
            'vehicle_id': self.vehicle_id,
            'position': self.position,
            'velocity': self.current_velocity,
            'direction': direction,
            'vehicle_type': self.vehicle_type,
            'state': self.state.value,
            'eta_to_intersection': self._calculate_eta(),
            'timestamp': current_time,
            'can_cross': self.can_cross,
            'priority': self.priority,
        }

    def reset_communication_flags(self, current_time: float) -> None:
        """Reset communication timestamps"""
        self.last_v2v_update = current_time
        self.last_v2i_update = current_time

    def get_trajectory_data(self) -> Dict:
        """Get trajectory data for analysis"""
        return {
            'vehicle_id': self.vehicle_id,
            'start_position': self.start_position,
            'end_position': self.position,
            'trajectory': self.trajectory,
            'velocity_history': self.velocity_history,
            'state_history': self.state_history,
            'total_distance': self.distance_traveled,
            'vehicle_type': self.vehicle_type,
            'crossing_completed': self.crossing_completed,
        }
