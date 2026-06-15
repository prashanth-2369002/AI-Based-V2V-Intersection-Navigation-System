"""
FCFS (First-Come-First-Serve) Scheduling Module
Standalone priority scheduler for intersection management.

Decoupled from RSU networking concerns so it can be tested and
benchmarked independently, or swapped for a different policy.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import time


@dataclass
class VehicleEntry:
    """A single entry in the FCFS queue."""
    vehicle_id: str
    arrival_time: float
    eta_to_intersection: float
    vehicle_type: str = "regular"
    priority_level: int = -1       # -1 = not yet assigned
    is_crossing: bool = False
    enqueue_time: float = field(default_factory=time.time)

    # Emergency vehicles jump the queue
    EMERGENCY_BOOST = 0


class FCFSScheduler:
    """
    First-Come-First-Serve intersection scheduler.

    Rules:
    - Vehicles are ranked by arrival_time (earliest first).
    - Emergency vehicles receive a scheduling boost (treated as arriving
      earlier than their actual timestamp).
    - At most `max_concurrent` vehicles may cross simultaneously.
    - A vehicle's priority_level is 1 (cross) or 0 (wait).
    """

    def __init__(self, max_concurrent: int = 1):
        """
        Args:
            max_concurrent: Maximum vehicles allowed to cross at the same time.
                            Set to 1 for strict FCFS; >1 for parallel non-conflicting lanes.
        """
        self.max_concurrent = max_concurrent
        self.queue: Dict[str, VehicleEntry] = {}        # all registered vehicles
        self.crossing_now: List[str] = []               # currently crossing
        self.completed: List[str] = []                  # finished crossing

        self._decision_log: List[Dict] = []

    # ------------------------------------------------------------------
    # Queue Management
    # ------------------------------------------------------------------

    def add_vehicle(self, vehicle_id: str, arrival_time: float,
                    eta_to_intersection: float,
                    vehicle_type: str = "regular") -> VehicleEntry:
        """
        Register a new vehicle in the scheduler.

        Args:
            vehicle_id:            Unique identifier.
            arrival_time:          Simulation time at which the vehicle first
                                   appeared in communication range.
            eta_to_intersection:   Estimated seconds until intersection entry.
            vehicle_type:          'regular' | 'emergency' | 'heavy'

        Returns:
            The created VehicleEntry (unassigned priority).
        """
        if vehicle_id in self.queue:
            return self.queue[vehicle_id]

        entry = VehicleEntry(
            vehicle_id=vehicle_id,
            arrival_time=arrival_time,
            eta_to_intersection=eta_to_intersection,
            vehicle_type=vehicle_type,
        )
        self.queue[vehicle_id] = entry
        return entry

    def update_eta(self, vehicle_id: str, new_eta: float) -> None:
        """Update a vehicle's ETA estimate (e.g., after deceleration)."""
        if vehicle_id in self.queue:
            self.queue[vehicle_id].eta_to_intersection = new_eta

    def complete_vehicle(self, vehicle_id: str) -> None:
        """Mark a vehicle as having finished crossing."""
        if vehicle_id in self.crossing_now:
            self.crossing_now.remove(vehicle_id)
        if vehicle_id in self.queue:
            self.completed.append(vehicle_id)
            del self.queue[vehicle_id]

    # ------------------------------------------------------------------
    # Priority Assignment
    # ------------------------------------------------------------------

    def assign_priorities(self, current_time: float) -> Dict[str, int]:
        """
        Run one FCFS assignment cycle.

        Sorts eligible vehicles by effective arrival time, assigns
        priority=1 to the first vehicle(s) up to max_concurrent if
        no conflicting crossing is already in progress.

        Returns:
            Dict mapping vehicle_id → priority level (1=cross, 0=wait).
        """
        decisions: Dict[str, int] = {}

        # Eligible = registered, not currently crossing, ETA is finite
        eligible = [
            entry for entry in self.queue.values()
            if entry.vehicle_id not in self.crossing_now
            and entry.eta_to_intersection < float("inf")
        ]

        # Sort by effective arrival time (emergency gets a 10-second boost)
        eligible.sort(key=lambda e: self._effective_arrival(e))

        slots_available = self.max_concurrent - len(self.crossing_now)

        for idx, entry in enumerate(eligible):
            if idx < slots_available:
                priority = 1
                entry.is_crossing = True
                self.crossing_now.append(entry.vehicle_id)
            else:
                priority = 0

            entry.priority_level = priority
            decisions[entry.vehicle_id] = priority

            self._decision_log.append({
                "timestamp": current_time,
                "vehicle_id": entry.vehicle_id,
                "priority": priority,
                "arrival_time": entry.arrival_time,
                "vehicle_type": entry.vehicle_type,
                "effective_arrival": self._effective_arrival(entry),
            })

        return decisions

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def get_queue_snapshot(self) -> List[Dict]:
        """Return a sorted snapshot of the current queue (for logging/debug)."""
        entries = sorted(
            self.queue.values(),
            key=lambda e: self._effective_arrival(e)
        )
        return [
            {
                "vehicle_id": e.vehicle_id,
                "arrival_time": e.arrival_time,
                "eta": e.eta_to_intersection,
                "vehicle_type": e.vehicle_type,
                "priority_level": e.priority_level,
                "is_crossing": e.is_crossing,
            }
            for e in entries
        ]

    def get_statistics(self) -> Dict:
        """Return scheduler statistics for evaluation."""
        total_decisions = len(self._decision_log)
        approved = sum(1 for d in self._decision_log if d["priority"] == 1)
        denied = total_decisions - approved

        return {
            "total_vehicles_registered": len(self.queue) + len(self.completed),
            "vehicles_completed": len(self.completed),
            "currently_crossing": len(self.crossing_now),
            "queue_length": len(self.queue),
            "total_decisions": total_decisions,
            "approved_crossings": approved,
            "denied_crossings": denied,
            "max_concurrent": self.max_concurrent,
        }

    def get_decision_log(self) -> List[Dict]:
        """Return full decision history (useful for audit/evaluation)."""
        return list(self._decision_log)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _effective_arrival(self, entry: VehicleEntry) -> float:
        """
        Compute the effective arrival time used for sorting.

        Emergency vehicles are treated as having arrived 10 seconds
        earlier than their actual timestamp, boosting them to the front.
        """
        if entry.vehicle_type == "emergency":
            return entry.arrival_time - 10.0
        return entry.arrival_time

    def __len__(self) -> int:
        return len(self.queue)

    def __repr__(self) -> str:
        return (
            f"FCFSScheduler(queued={len(self.queue)}, "
            f"crossing={len(self.crossing_now)}, "
            f"completed={len(self.completed)})"
        )
