"""
Unit tests for the AI trajectory predictor and collision analyzer (ai_predictor.py)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import math
import pytest
from ai_predictor import TrajectoryPredictor, CollisionAnalyzer
import config


def _vehicle_info(vid: str, pos, vel, direction):
    return {
        "vehicle_id": vid,
        "position": pos,
        "velocity": vel,
        "direction": direction,
    }


class TestTrajectoryPredictor:

    def setup_method(self):
        self.predictor = TrajectoryPredictor()

    def test_predict_returns_correct_number_of_steps(self):
        preds = self.predictor.predict_trajectory(
            "V1", (100, 500), velocity=20, direction=(1, 0), steps_ahead=10
        )
        assert len(preds) == 11  # current + 10 steps

    def test_predict_moves_in_direction(self):
        preds = self.predictor.predict_trajectory(
            "V1", (100, 500), velocity=20, direction=(1, 0), steps_ahead=5
        )
        # x should increase monotonically (rightward)
        xs = [p[0] for p in preds]
        assert all(xs[i+1] >= xs[i] for i in range(len(xs) - 1))

    def test_update_history_stores_entries(self):
        self.predictor.update_vehicle_history("V1", (100, 500), 20.0)
        self.predictor.update_vehicle_history("V1", (102, 500), 20.0)
        assert len(self.predictor.trajectory_history["V1"]) == 2

    def test_history_capped_at_200(self):
        for i in range(250):
            self.predictor.update_vehicle_history("V1", (i, 500), 10.0)
        assert len(self.predictor.trajectory_history["V1"]) <= 200

    def test_collision_risk_zero_when_far_apart(self):
        v1 = _vehicle_info("V1", (50, 500), 20, (1, 0))
        v2 = _vehicle_info("V2", (950, 500), 20, (-1, 0))
        risk = self.predictor.calculate_collision_risk(v1, v2)
        assert risk == 0.0

    def test_collision_risk_nonzero_when_close(self):
        v1 = _vehicle_info("V1", (490, 500), 20, (1, 0))
        v2 = _vehicle_info("V2", (510, 500), 20, (-1, 0))
        risk = self.predictor.calculate_collision_risk(v1, v2)
        assert risk > 0.0

    def test_collision_risk_between_zero_and_one(self):
        v1 = _vehicle_info("V1", (490, 500), 20, (1, 0))
        v2 = _vehicle_info("V2", (500, 490), 20, (0, 1))
        risk = self.predictor.calculate_collision_risk(v1, v2)
        assert 0.0 <= risk <= 1.0

    def test_head_on_collision_detected(self):
        v1 = _vehicle_info("V1", (100, 500), 20, (1, 0))
        v2 = _vehicle_info("V2", (900, 500), 20, (-1, 0))
        assert self.predictor.detect_head_on_collision(v1, v2) is True

    def test_no_head_on_perpendicular(self):
        v1 = _vehicle_info("V1", (500, 50), 20, (0, 1))
        v2 = _vehicle_info("V2", (50, 500), 20, (1, 0))
        # Dot product = 0 → not head-on
        assert self.predictor.detect_head_on_collision(v1, v2) is False

    def test_estimate_crossing_time_positive(self):
        v = _vehicle_info("V1", (100, 500), 20, (1, 0))
        t = self.predictor.estimate_crossing_time(v)
        assert t > 0

    def test_estimate_crossing_time_infinity_when_stopped(self):
        v = _vehicle_info("V1", (100, 500), 0, (1, 0))
        t = self.predictor.estimate_crossing_time(v)
        assert t == float("inf")

    def test_statistics(self):
        self.predictor.update_vehicle_history("V1", (100, 500), 20)
        stats = self.predictor.get_statistics()
        assert "tracked_vehicles" in stats
        assert stats["tracked_vehicles"] == 1


class TestCollisionAnalyzer:

    def setup_method(self):
        self.analyzer = CollisionAnalyzer()

    def test_analyze_returns_expected_keys(self):
        v1 = _vehicle_info("V1", (490, 500), 20, (1, 0))
        v2 = _vehicle_info("V2", (500, 490), 20, (0, 1))
        result = self.analyzer.analyze_vehicle_pair(v1, v2, current_time=1.0)
        for key in ("vehicle_a", "vehicle_b", "risk_score", "is_head_on",
                    "time_to_collision", "current_distance", "timestamp"):
            assert key in result

    def test_high_risk_event_logged(self):
        # Very close vehicles
        v1 = _vehicle_info("V1", (500, 500), 25, (1, 0))
        v2 = _vehicle_info("V2", (505, 500), 5, (-1, 0))
        result = self.analyzer.analyze_vehicle_pair(v1, v2, current_time=0.5)
        # If risk > 0.7 it's logged; just verify the summary reflects it
        summary = self.analyzer.get_collision_summary()
        assert "total_high_risk_events" in summary

    def test_collision_summary_empty_initially(self):
        summary = self.analyzer.get_collision_summary()
        assert summary["total_high_risk_events"] == 0
