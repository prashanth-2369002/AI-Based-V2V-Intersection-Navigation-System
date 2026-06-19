"""
Unit tests for the standalone FCFS Scheduler (fcfs.py)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fcfs import FCFSScheduler, VehicleEntry


class TestFCFSScheduler:

    def setup_method(self):
        self.scheduler = FCFSScheduler(max_concurrent=1)

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def test_add_vehicle_returns_entry(self):
        entry = self.scheduler.add_vehicle("V1", arrival_time=0.5, eta_to_intersection=5.0)
        assert isinstance(entry, VehicleEntry)
        assert entry.vehicle_id == "V1"

    def test_add_duplicate_vehicle_returns_same_entry(self):
        e1 = self.scheduler.add_vehicle("V1", arrival_time=0.5, eta_to_intersection=5.0)
        e2 = self.scheduler.add_vehicle("V1", arrival_time=0.5, eta_to_intersection=5.0)
        assert e1 is e2

    def test_queue_length(self):
        self.scheduler.add_vehicle("V1", 0.0, 5.0)
        self.scheduler.add_vehicle("V2", 0.1, 6.0)
        assert len(self.scheduler) == 2

    # ------------------------------------------------------------------
    # FCFS ordering
    # ------------------------------------------------------------------

    def test_earlier_arrival_gets_priority_one(self):
        self.scheduler.add_vehicle("V2", arrival_time=0.3, eta_to_intersection=6.0)
        self.scheduler.add_vehicle("V1", arrival_time=0.1, eta_to_intersection=5.0)

        decisions = self.scheduler.assign_priorities(current_time=1.0)

        assert decisions["V1"] == 1, "V1 arrived first — should cross"
        assert decisions["V2"] == 0, "V2 arrived later — should wait"

    def test_later_arrival_waits(self):
        self.scheduler.add_vehicle("VA", 1.0, 4.0)
        self.scheduler.add_vehicle("VB", 2.0, 4.0)

        decisions = self.scheduler.assign_priorities(current_time=2.0)

        assert decisions["VA"] == 1
        assert decisions["VB"] == 0

    def test_three_vehicles_only_first_crosses(self):
        for i, t in enumerate([0.5, 1.0, 1.5]):
            self.scheduler.add_vehicle(f"V{i + 1}", arrival_time=t, eta_to_intersection=5.0)

        decisions = self.scheduler.assign_priorities(current_time=2.0)

        assert decisions["V1"] == 1
        assert decisions["V2"] == 0
        assert decisions["V3"] == 0

    # ------------------------------------------------------------------
    # Completion and re-queuing
    # ------------------------------------------------------------------

    def test_completion_removes_from_queue(self):
        self.scheduler.add_vehicle("V1", 0.0, 5.0)
        self.scheduler.assign_priorities(0.5)
        self.scheduler.complete_vehicle("V1")

        assert "V1" not in self.scheduler.queue
        assert "V1" in self.scheduler.completed

    def test_next_vehicle_gets_priority_after_completion(self):
        self.scheduler.add_vehicle("V1", 0.0, 5.0)
        self.scheduler.add_vehicle("V2", 0.2, 5.0)

        self.scheduler.assign_priorities(0.5)
        self.scheduler.complete_vehicle("V1")

        decisions = self.scheduler.assign_priorities(1.0)
        assert decisions["V2"] == 1

    def test_max_concurrent_two(self):
        sched = FCFSScheduler(max_concurrent=2)
        sched.add_vehicle("V1", 0.0, 4.0)
        sched.add_vehicle("V2", 0.1, 4.0)
        sched.add_vehicle("V3", 0.2, 4.0)

        decisions = sched.assign_priorities(0.5)

        assert decisions["V1"] == 1
        assert decisions["V2"] == 1
        assert decisions["V3"] == 0

    # ------------------------------------------------------------------
    # Emergency vehicle boost
    # ------------------------------------------------------------------

    def test_emergency_vehicle_preempts_regular(self):
        self.scheduler.add_vehicle("V_reg", arrival_time=0.1,
                                   eta_to_intersection=4.0, vehicle_type="regular")
        self.scheduler.add_vehicle("V_em", arrival_time=0.5,
                                   eta_to_intersection=3.0, vehicle_type="emergency")

        decisions = self.scheduler.assign_priorities(1.0)

        assert decisions["V_em"] == 1, "Emergency vehicle should jump the queue"
        assert decisions["V_reg"] == 0

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    def test_statistics_after_run(self):
        self.scheduler.add_vehicle("V1", 0.0, 5.0)
        self.scheduler.add_vehicle("V2", 0.1, 5.0)
        self.scheduler.assign_priorities(0.5)
        self.scheduler.complete_vehicle("V1")

        stats = self.scheduler.get_statistics()

        assert stats["total_decisions"] == 2
        assert stats["approved_crossings"] == 1
        assert stats["denied_crossings"] == 1
        assert stats["vehicles_completed"] == 1

    def test_queue_snapshot_sorted(self):
        self.scheduler.add_vehicle("V3", 0.9, 5.0)
        self.scheduler.add_vehicle("V1", 0.1, 5.0)
        self.scheduler.add_vehicle("V2", 0.5, 5.0)

        snapshot = self.scheduler.get_queue_snapshot()
        ids = [e["vehicle_id"] for e in snapshot]

        assert ids == ["V1", "V2", "V3"]

    # ------------------------------------------------------------------
    # ETA update
    # ------------------------------------------------------------------

    def test_update_eta(self):
        self.scheduler.add_vehicle("V1", 0.0, 10.0)
        self.scheduler.update_eta("V1", 3.0)
        assert self.scheduler.queue["V1"].eta_to_intersection == 3.0
