"""
Unit tests for the RSU module (rsu.py)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from rsu import RSU, RSUState, VehicleEntry


def _make_vehicle_info(vid: str, arrival_offset: float = 0.0,
                        position=(450, 500), velocity=20.0) -> dict:
    return {
        "vehicle_id": vid,
        "position": position,
        "velocity": velocity,
        "vehicle_type": "regular",
        "eta_to_intersection": 5.0 + arrival_offset,
    }


class TestRSURegistration:

    def setup_method(self):
        self.rsu = RSU()

    def test_register_single_vehicle(self):
        info = _make_vehicle_info("V1", 0.0)
        self.rsu.register_vehicle(info, current_time=0.0)
        assert "V1" in self.rsu.vehicle_registry

    def test_register_same_vehicle_twice_is_idempotent(self):
        info = _make_vehicle_info("V1")
        self.rsu.register_vehicle(info, 0.0)
        self.rsu.register_vehicle(info, 0.5)
        assert len(self.rsu.vehicle_registry) == 1

    def test_register_multiple_vehicles(self):
        for i in range(3):
            self.rsu.register_vehicle(_make_vehicle_info(f"V{i+1}"), float(i))
        assert len(self.rsu.vehicle_registry) == 3

    def test_update_vehicle_info_changes_velocity(self):
        self.rsu.register_vehicle(_make_vehicle_info("V1"), 0.0)
        updated = _make_vehicle_info("V1", velocity=35.0)
        self.rsu.update_vehicle_info(updated, 0.5)
        assert self.rsu.vehicle_registry["V1"].velocity == 35.0


class TestFCFSDecision:

    def setup_method(self):
        self.rsu = RSU()

    def _register_and_decide(self, num_vehicles: int = 2) -> dict:
        for i in range(num_vehicles):
            info = _make_vehicle_info(f"V{i+1}", arrival_offset=i * 0.1)
            self.rsu.register_vehicle(info, current_time=float(i) * 0.1)
        return self.rsu.make_priority_decision(current_time=1.0)

    def test_first_registered_gets_priority_one(self):
        decisions = self._register_and_decide(2)
        assert decisions.get("V1") == 1

    def test_second_vehicle_waits(self):
        decisions = self._register_and_decide(2)
        assert decisions.get("V2") == 0

    def test_no_vehicles_returns_empty_dict(self):
        decisions = self.rsu.make_priority_decision(current_time=0.0)
        assert decisions == {}

    def test_state_becomes_decision_made(self):
        self.rsu.register_vehicle(_make_vehicle_info("V1"), 0.0)
        self.rsu.make_priority_decision(1.0)
        assert self.rsu.state == RSUState.DECISION_MADE

    def test_decisions_are_logged(self):
        self._register_and_decide(2)
        log = self.rsu.get_detailed_decisions()
        assert len(log) == 2

    def test_get_vehicle_priority_returns_assigned_level(self):
        self._register_and_decide(2)
        assert self.rsu.get_vehicle_priority("V1") == 1
        assert self.rsu.get_vehicle_priority("V2") == 0

    def test_unknown_vehicle_returns_minus_one(self):
        assert self.rsu.get_vehicle_priority("GHOST") == -1


class TestCollisionDetection:

    def setup_method(self):
        self.rsu = RSU()

    def test_no_collision_when_far_apart(self):
        v1 = {"vehicle_id": "V1", "position": (100, 500), "velocity": 20.0}
        v2 = {"vehicle_id": "V2", "position": (900, 500), "velocity": 20.0}
        risks = self.rsu.detect_collision_risk([v1, v2])
        assert risks == []

    def test_collision_detected_when_close(self):
        v1 = {"vehicle_id": "V1", "position": (500, 500), "velocity": 30.0}
        v2 = {"vehicle_id": "V2", "position": (510, 510), "velocity": 10.0}
        risks = self.rsu.detect_collision_risk([v1, v2])
        assert len(risks) == 1
        assert risks[0]["risk_score"] > 0.0

    def test_risk_score_between_zero_and_one(self):
        v1 = {"vehicle_id": "V1", "position": (505, 500), "velocity": 25.0}
        v2 = {"vehicle_id": "V2", "position": (495, 500), "velocity": 5.0}
        risks = self.rsu.detect_collision_risk([v1, v2])
        if risks:
            assert 0.0 <= risks[0]["risk_score"] <= 1.0


class TestRSUStatistics:

    def setup_method(self):
        self.rsu = RSU()
        for i in range(2):
            self.rsu.register_vehicle(_make_vehicle_info(f"V{i+1}"), float(i))
        self.rsu.make_priority_decision(1.0)

    def test_statistics_contain_expected_keys(self):
        stats = self.rsu.get_statistics()
        for key in ("rsu_id", "total_vehicles_managed", "vehicles_crossed",
                    "total_decisions", "collision_detections", "avg_processing_time"):
            assert key in stats

    def test_remove_completed_vehicle(self):
        self.rsu.remove_completed_vehicle("V1")
        assert "V1" not in self.rsu.active_vehicles
        assert "V1" not in self.rsu.current_crossing_vehicles
