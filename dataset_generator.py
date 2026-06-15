"""
Synthetic Dataset Generator
Generates labelled CSV datasets from simulation runs for ML training and
offline benchmarking.

Each row represents one vehicle at one simulation timestep.

Columns:
    sample_id, scenario_id, step, vehicle_id,
    position_x, position_y,
    velocity, direction_x, direction_y,
    eta_to_intersection,
    distance_to_intersection,
    arrival_time,
    vehicle_type,
    priority_assigned,          ← label: 1 = cross, 0 = wait
    collision_risk_score,       ← label: continuous [0, 1]
    state                       ← label: approaching/waiting/crossing/completed
"""

import argparse
import csv
import json
import math
import os
import random
from datetime import datetime
from typing import Dict, List, Tuple

import config
from simulation import SimulationEngine
from ai_predictor import TrajectoryPredictor


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

INTERSECTION = config.INTERSECTION_CENTER

def _dist(pos: Tuple[float, float]) -> float:
    return math.sqrt((pos[0] - INTERSECTION[0])**2 + (pos[1] - INTERSECTION[1])**2)


def _direction_from_start(start: Tuple[float, float]) -> Tuple[float, float]:
    dx = INTERSECTION[0] - start[0]
    dy = INTERSECTION[1] - start[1]
    mag = math.sqrt(dx**2 + dy**2) or 1.0
    return (dx / mag, dy / mag)


# ---------------------------------------------------------------------------
# Single-run data extraction
# ---------------------------------------------------------------------------

def extract_samples_from_results(results: Dict, scenario_id: int,
                                 predictor: TrajectoryPredictor) -> List[Dict]:
    """
    Convert a simulation results dict into flat row dicts.

    One row per (vehicle, timestep) where the vehicle is not IDLE.
    """
    rows: List[Dict] = []
    trajectories = results.get("vehicle_trajectories", {})
    collision_events = {
        e["vehicle_a"] for e in results.get("collision_analysis", {}).get("collision_events", [])
    }

    for vehicle_id, traj_data in trajectories.items():
        trajectory: List = traj_data.get("trajectory", [])
        velocity_history: List = traj_data.get("velocity_history", [])
        state_history: List = traj_data.get("state_history", [])
        start_pos = traj_data.get("start_position", trajectory[0] if trajectory else (0, 0))
        vehicle_type = traj_data.get("vehicle_type", "regular")
        arrival_time = float(state_history[0][0]) if state_history else 0.0

        direction = _direction_from_start(start_pos)

        n = min(len(trajectory), len(velocity_history))
        for step in range(n):
            pos = trajectory[step]
            vel = velocity_history[step]
            dist_to_int = _dist(pos)

            if vel > 0:
                eta = dist_to_int / vel
            else:
                eta = float("inf") if dist_to_int > 5 else 0.0

            # Determine state label from state_history (approximation)
            state_label = "approaching"
            for (ts, st) in reversed(state_history):
                if step * config.TIME_STEP_DURATION >= ts:
                    state_label = str(st).split(".")[-1].lower()
                    break

            # Priority label: 1 if vehicle eventually crossed
            priority_label = 1 if traj_data.get("crossing_completed", False) else 0

            # Collision risk: 1 if this vehicle appears in collision events
            risk = 0.8 if vehicle_id in collision_events else random.uniform(0.0, 0.15)

            rows.append({
                "sample_id": f"{scenario_id}_{vehicle_id}_{step}",
                "scenario_id": scenario_id,
                "step": step,
                "vehicle_id": vehicle_id,
                "position_x": round(pos[0], 4),
                "position_y": round(pos[1], 4),
                "velocity": round(vel, 4),
                "direction_x": round(direction[0], 4),
                "direction_y": round(direction[1], 4),
                "eta_to_intersection": round(eta, 4) if eta != float("inf") else -1.0,
                "distance_to_intersection": round(dist_to_int, 4),
                "arrival_time": round(arrival_time, 4),
                "vehicle_type": vehicle_type,
                "priority_assigned": priority_label,
                "collision_risk_score": round(risk, 4),
                "state": state_label,
            })

    return rows


# ---------------------------------------------------------------------------
# Multi-run generator
# ---------------------------------------------------------------------------

FIELDNAMES = [
    "sample_id", "scenario_id", "step", "vehicle_id",
    "position_x", "position_y",
    "velocity", "direction_x", "direction_y",
    "eta_to_intersection", "distance_to_intersection",
    "arrival_time", "vehicle_type",
    "priority_assigned", "collision_risk_score", "state",
]


def generate_dataset(num_samples: int, output_path: str,
                     scenarios: List[str] = None) -> None:
    """
    Run multiple simulations and write all rows to a CSV file.

    Args:
        num_samples:  Approximate total number of rows (rows ≈ vehicles × steps × runs).
        output_path:  Destination CSV file path.
        scenarios:    List of scenario names to cycle through.
                      Defaults to all scenarios in config.
    """
    if scenarios is None:
        scenarios = list(config.SCENARIOS.keys())

    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)

    predictor = TrajectoryPredictor()
    all_rows: List[Dict] = []
    scenario_id = 0

    print(f"Generating dataset — target ≈ {num_samples} rows …")

    while len(all_rows) < num_samples:
        scenario_name = scenarios[scenario_id % len(scenarios)]

        # Vary speeds slightly for diversity
        original_config = config.SCENARIOS[scenario_name].copy()
        speeds = original_config.get("vehicle_speeds", [25, 25])
        jittered_speeds = [
            max(config.VEHICLE_SPEED_MIN,
                min(config.VEHICLE_SPEED_MAX, s + random.randint(-5, 5)))
            for s in speeds
        ]
        config.SCENARIOS[scenario_name]["vehicle_speeds"] = jittered_speeds

        try:
            engine = SimulationEngine(scenario=scenario_name)
            results = engine.run_simulation()
            rows = extract_samples_from_results(results, scenario_id, predictor)
            all_rows.extend(rows)
        except Exception as exc:
            print(f"  [WARN] Scenario {scenario_name} failed: {exc}")
        finally:
            config.SCENARIOS[scenario_name]["vehicle_speeds"] = speeds  # restore

        scenario_id += 1

        if scenario_id % 5 == 0:
            print(f"  Generated {len(all_rows)} rows so far …")

    # Trim to requested size
    all_rows = all_rows[:num_samples]
    random.shuffle(all_rows)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"\nDataset written: {output_path}")
    print(f"  Rows:     {len(all_rows)}")
    print(f"  Columns:  {len(FIELDNAMES)}")
    print(f"  Scenarios cycled: {scenario_id}")
    _print_label_distribution(all_rows)


def _print_label_distribution(rows: List[Dict]) -> None:
    """Print a summary of label distributions in the dataset."""
    n = len(rows) or 1
    p1 = sum(1 for r in rows if r["priority_assigned"] == 1)
    p0 = n - p1
    high_risk = sum(1 for r in rows if r["collision_risk_score"] > 0.5)
    states = {}
    for r in rows:
        states[r["state"]] = states.get(r["state"], 0) + 1

    print(f"\n  Label distribution:")
    print(f"    priority=1 (cross): {p1} ({p1/n:.1%})")
    print(f"    priority=0 (wait):  {p0} ({p0/n:.1%})")
    print(f"    high risk (>0.5):   {high_risk} ({high_risk/n:.1%})")
    print(f"    states: {states}")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate synthetic V2V intersection dataset"
    )
    parser.add_argument(
        "--samples", type=int, default=500,
        help="Approximate number of rows to generate (default: 500)"
    )
    parser.add_argument(
        "--output", default="data/dataset.csv",
        help="Output CSV file path (default: data/dataset.csv)"
    )
    parser.add_argument(
        "--scenarios", nargs="+",
        default=None,
        help="Scenario names to cycle through (default: all)"
    )
    args = parser.parse_args()

    print("=" * 60)
    print("V2V INTERSECTION DATASET GENERATOR")
    print("=" * 60)
    print(f"Target rows:   {args.samples}")
    print(f"Output file:   {args.output}")
    print(f"Scenarios:     {args.scenarios or list(config.SCENARIOS.keys())}")
    print()

    generate_dataset(
        num_samples=args.samples,
        output_path=args.output,
        scenarios=args.scenarios,
    )


if __name__ == "__main__":
    main()
