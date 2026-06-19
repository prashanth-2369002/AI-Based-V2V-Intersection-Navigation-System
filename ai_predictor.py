"""
AI-based trajectory prediction and collision risk analysis
"""

import math
from typing import Dict, List, Tuple

import config


class TrajectoryPredictor:
    """Predicts vehicle trajectories using exponential smoothing and physics"""

    def __init__(self):
        self.trajectory_history: Dict[str, List[Tuple[float, float]]] = {}
        self.velocity_history: Dict[str, List[float]] = {}
        self.predictions: Dict[str, List[Tuple[float, float]]] = {}

    def update_vehicle_history(self, vehicle_id: str, position: Tuple[float, float],
                               velocity: float) -> None:
        """Update position and velocity history for a vehicle"""
        if vehicle_id not in self.trajectory_history:
            self.trajectory_history[vehicle_id] = []
            self.velocity_history[vehicle_id] = []

        self.trajectory_history[vehicle_id].append(position)
        self.velocity_history[vehicle_id].append(velocity)

        # Keep only recent history to avoid memory issues
        max_history = 200
        if len(self.trajectory_history[vehicle_id]) > max_history:
            self.trajectory_history[vehicle_id] = self.trajectory_history[vehicle_id][-max_history:]
            self.velocity_history[vehicle_id] = self.velocity_history[vehicle_id][-max_history:]

    def predict_trajectory(self, vehicle_id: str, current_position: Tuple[float, float],
                          velocity: float, direction: Tuple[float, float],
                          steps_ahead: int = 10) -> List[Tuple[float, float]]:
        """
        Predict future positions of a vehicle
        
        Args:
            vehicle_id: Vehicle identifier
            current_position: Current position (x, y)
            velocity: Current velocity
            direction: Direction unit vector
            steps_ahead: Number of time steps to predict
            
        Returns:
            List of predicted positions
        """
        predictions = [current_position]

        x, y = current_position
        current_vel = velocity

        for step in range(steps_ahead):
            # Apply exponential smoothing if history exists
            if vehicle_id in self.velocity_history and len(self.velocity_history[vehicle_id]) > 1:
                smoothed_vel = self._exponential_smooth(
                    self.velocity_history[vehicle_id],
                    config.TRAJECTORY_SMOOTHING
                )
                current_vel = smoothed_vel

            # Update position
            dx = direction[0] * current_vel * config.TIME_STEP_DURATION
            dy = direction[1] * current_vel * config.TIME_STEP_DURATION

            x += dx
            y += dy
            predictions.append((x, y))

        self.predictions[vehicle_id] = predictions
        return predictions

    def calculate_collision_risk(self, vehicle_a: Dict, vehicle_b: Dict,
                                 prediction_window: int = 10) -> float:
        """
        Calculate collision risk between two vehicles
        
        Args:
            vehicle_a: First vehicle data with position, velocity, direction
            vehicle_b: Second vehicle data with position, velocity, direction
            prediction_window: Steps ahead to evaluate
            
        Returns:
            Collision risk score (0.0 to 1.0)
        """
        risk_score = 0.0
        min_distances = []

        # Predict both vehicles' trajectories
        pred_a = self.predict_trajectory(
            f"{vehicle_a['vehicle_id']}_pred",
            vehicle_a['position'],
            vehicle_a['velocity'],
            vehicle_a['direction'],
            steps_ahead=prediction_window
        )

        pred_b = self.predict_trajectory(
            f"{vehicle_b['vehicle_id']}_pred",
            vehicle_b['position'],
            vehicle_b['velocity'],
            vehicle_b['direction'],
            steps_ahead=prediction_window
        )

        # Calculate minimum distance during prediction window
        for pos_a, pos_b in zip(pred_a, pred_b):
            distance = self._euclidean_distance(pos_a, pos_b)
            min_distances.append(distance)

        min_distance = min(min_distances) if min_distances else float('inf')

        # Risk calculation: higher risk if closer
        if min_distance < config.COLLISION_THRESHOLD:
            risk_score = 1.0 - (min_distance / config.COLLISION_THRESHOLD)
        else:
            # Low risk if far apart
            risk_score = 0.0

        # Consider trajectory convergence
        initial_distance = self._euclidean_distance(vehicle_a['position'], vehicle_b['position'])
        if min_distance < initial_distance:
            # Trajectories converging, increase risk slightly
            convergence_factor = 1.2
            risk_score = min(1.0, risk_score * convergence_factor)

        return risk_score

    def detect_head_on_collision(self, vehicle_a: Dict, vehicle_b: Dict) -> bool:
        """Detect if vehicles are on a head-on collision course"""
        # Calculate angle between velocity vectors
        dot_product = (
            vehicle_a['direction'][0] * vehicle_b['direction'][0] +
            vehicle_a['direction'][1] * vehicle_b['direction'][1]
        )

        # If dot product is negative, vehicles moving toward each other
        if dot_product < -0.7:
            return True

        return False

    def estimate_crossing_time(self, vehicle_data: Dict) -> float:
        """Estimate time for vehicle to cross the intersection"""
        distance_to_intersection = self._distance_to_intersection(vehicle_data['position'])

        if vehicle_data['velocity'] > 0:
            return distance_to_intersection / vehicle_data['velocity']
        return float('inf')

    def calculate_trajectory_divergence(self, vehicle_a_trajectory: List[Tuple[float, float]],
                                       vehicle_b_trajectory: List[Tuple[float, float]]) -> float:
        """Calculate how much two trajectories diverge"""
        if not vehicle_a_trajectory or not vehicle_b_trajectory:
            return 0.0

        # Calculate average distance between corresponding trajectory points
        distances = []
        for i in range(min(len(vehicle_a_trajectory), len(vehicle_b_trajectory))):
            dist = self._euclidean_distance(
                vehicle_a_trajectory[i],
                vehicle_b_trajectory[i]
            )
            distances.append(dist)

        return sum(distances) / len(distances) if distances else 0.0

    def _exponential_smooth(self, values: List[float], alpha: float = 0.3) -> float:
        """Apply exponential smoothing to a series of values"""
        if not values:
            return 0.0

        smoothed = values[0]
        for value in values[1:]:
            smoothed = alpha * value + (1 - alpha) * smoothed

        return smoothed

    def _euclidean_distance(self, pos1: Tuple[float, float],
                           pos2: Tuple[float, float]) -> float:
        """Calculate Euclidean distance"""
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

    def _distance_to_intersection(self, position: Tuple[float, float]) -> float:
        """Calculate distance to intersection center"""
        return self._euclidean_distance(position, config.INTERSECTION_CENTER)

    def get_statistics(self) -> Dict:
        """Get predictor statistics"""
        return {
            'tracked_vehicles': len(self.trajectory_history),
            'prediction_entries': sum(len(p) for p in self.predictions.values()),
        }


class CollisionAnalyzer:
    """Analyzes and predicts collisions using multiple methods"""

    def __init__(self):
        self.predictor = TrajectoryPredictor()
        self.collision_events: List[Dict] = []
        self.risk_history: Dict[Tuple[str, str], List[float]] = {}

    def analyze_vehicle_pair(self, vehicle_a: Dict, vehicle_b: Dict,
                            current_time: float) -> Dict:
        """
        Comprehensive collision analysis for a pair of vehicles
        
        Returns:
            Analysis result dictionary
        """
        pair_key = tuple(sorted([vehicle_a['vehicle_id'], vehicle_b['vehicle_id']]))

        # Calculate various risk metrics
        risk_score = self.predictor.calculate_collision_risk(vehicle_a, vehicle_b)
        is_head_on = self.predictor.detect_head_on_collision(vehicle_a, vehicle_b)
        time_to_collision = self._estimate_time_to_collision(vehicle_a, vehicle_b)

        # Initialize risk history if needed
        if pair_key not in self.risk_history:
            self.risk_history[pair_key] = []

        self.risk_history[pair_key].append(risk_score)

        analysis = {
            'vehicle_a': vehicle_a['vehicle_id'],
            'vehicle_b': vehicle_b['vehicle_id'],
            'risk_score': risk_score,
            'is_head_on': is_head_on,
            'time_to_collision': time_to_collision,
            'current_distance': self.predictor._euclidean_distance(
                vehicle_a['position'],
                vehicle_b['position']
            ),
            'velocity_a': vehicle_a['velocity'],
            'velocity_b': vehicle_b['velocity'],
            'timestamp': current_time,
        }

        # Log if high risk
        if risk_score > 0.7:
            self.collision_events.append(analysis)

        return analysis

    def _estimate_time_to_collision(self, vehicle_a: Dict, vehicle_b: Dict) -> float:
        """Estimate time until collision if no action taken"""
        # Simple relative velocity calculation
        rel_velocity = max(
            vehicle_a['velocity'],
            vehicle_b['velocity']
        )

        distance = self.predictor._euclidean_distance(
            vehicle_a['position'],
            vehicle_b['position']
        )

        if rel_velocity > 0:
            return distance / rel_velocity
        return float('inf')

    def get_collision_summary(self) -> Dict:
        """Get summary of collision analysis"""
        high_risk_count = len(self.collision_events)

        return {
            'total_high_risk_events': high_risk_count,
            'collision_events': self.collision_events,
        }
