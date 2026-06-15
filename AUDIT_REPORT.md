# Repository Audit Report

**Project:** AI-Based V2V Negotiation System for Safe Unsignalized Intersection Navigation
**Date:** 2026-06-12
**Scope:** `main.py`, `simulation.py`, `communication.py`, `vehicle.py`, `rsu.py`, `ai_predictor.py`, `visualizer.py`, `config.py`
**Status:** Audit only — no code changes made.

---

## Executive Summary

The simulation runs to completion without exceptions, but it does not do what the project claims to do. **No vehicle ever crosses the intersection in any recorded run** (`successful_crossings = 0` in all 16 data files), and the system deadlocks by design due to a chain of four interacting bugs:

1. **Priority messages from the RSU never reach vehicles** — the V2I channel's shared message queue is drained by the RSU read before vehicles can read their own messages (Critical C1).
2. **Vehicles brake to a stop in WAITING and can never recover** — once stopped, their ETA becomes infinite, which excludes them from all future RSU decisions (Critical C4).
3. **Vehicles steer toward the intersection center, never toward their destination** — even if granted priority, they could not pass through and exit (Critical C2).
4. **The post-intersection target is computed on the wrong side of the map** — destinations are behind the spawn point, off-grid (Critical C3).

Additionally, **V2V communication is decorative**: in the current code, vehicles broadcast and "receive" V2V messages (the older runs that showed `V2V Messages Sent = 0` predate the current `simulation.py`), but the received messages are stored and never acted upon. There is no vehicle-to-vehicle *negotiation* anywhere in the codebase — the project title is not implemented.

The latest data file (`data/simulation_scenario_1_20260612_140837.json`) confirms the symptoms: V1 frozen at (391.3, 500), V2 frozen at (610.9, 500) — both ~110 px short of the intersection — 180.4 s of accumulated wait time over a 100 s simulation, zero crossings.

**Findings: 6 Critical, 10 Medium, 9 Minor.**

---

## CRITICAL FINDINGS

### C1. RSU steals (and silently discards) the priority messages meant for vehicles

**Files:** `communication.py` — `CommunicationChannel.get_pending_messages()` (line 86), `V2ICommunication.get_rsu_messages()` (line 222), `V2ICommunication.get_vehicle_messages()` (line 226); `simulation.py` — `step()` Steps 5 and 7 (lines 148–185)

**Evidence:**

```python
# communication.py:222 — no receiver filter; returns EVERYTHING delivered
def get_rsu_messages(self, current_time: float) -> List[Message]:
    """Get messages received by RSU"""
    return self.channel.get_pending_messages(current_time)

# communication.py:86-99 — get_pending_messages() is destructive:
# every delivered message is removed from the queue regardless of addressee
for delivery_time, message in self.message_queue:
    if delivery_time <= current_time:
        self.received_messages.append(message)
        delivered.append(message)
    ...
self.message_queue = pending

# simulation.py:149-158 — Step 5 runs BEFORE Step 7 and silently drops
# anything without a 'vehicle_id' key — i.e., every {'priority': n} payload
rsu_messages = self.v2i_communication.get_rsu_messages(self.current_time)
for msg in rsu_messages:
    ...
    if isinstance(vehicle_info, dict) and 'vehicle_id' in vehicle_info:
        self.rsu.update_vehicle_info(vehicle_info, self.current_time)
```

**Runtime confirmation:** the `DEBUG: ... received priority` prints at `simulation.py:182,185` never appear in any run; `successful_crossings = 0` in all 16 data files.

**Root cause:** Both directions of V2I traffic (vehicle→RSU `VEHICLE_INFO` and RSU→vehicle `PRIORITY_ASSIGNMENT`) share **one** `CommunicationChannel` with **one** message queue. `get_pending_messages()` is destructive — it removes every delivered message from the queue regardless of addressee:

- `get_rsu_messages()` returns *all* delivered messages with no `receiver_id == "RSU"` filter. In `simulation.py` Step 5, the engine drains the queue, and the handler (`if isinstance(vehicle_info, dict) and 'vehicle_id' in vehicle_info`) silently drops anything that isn't vehicle info — i.e., every priority assignment, whose payload is just `{'priority': n}`.
- Priority decisions sent at step *N* are delivered (after the ~50–75 ms simulated delay) at step *N+1*, where Step 5 (RSU read) runs **before** Step 7 (vehicle read) and consumes them.

**Consequence:** `vehicle.can_cross` is never set to `True` for any vehicle. The `DEBUG:` print statements in Step 7 never fire. The entire RSU→vehicle control loop is severed. This is the primary root cause of "vehicles never complete crossing."

**Proposed fix:** Make message retrieval per-receiver: filter by `receiver_id` *inside* the channel and only remove the matching messages from the queue (or maintain a per-receiver inbox dict). `get_rsu_messages()` should return only `receiver_id == "RSU"` messages. Alternatively, use two separate channels for uplink and downlink.

---

### C2. Vehicles steer toward the intersection center forever — crossing and exit are geometrically impossible

**File:** `vehicle.py` — `update()` line 88, `_update_position()` (lines 145–154)

**Evidence:**

```python
# vehicle.py:88 — first line of update(): heading is ALWAYS toward the center,
# in every state, every step; self.target_position is never used for steering
def update(self, current_time: float, collision_risk: float = 0.0) -> None:
    direction = self._calculate_direction(self.position, config.INTERSECTION_CENTER)
```

`target_position` appears in `vehicle.py` only in `__init__` and in the completion-distance heuristic (`_update_state()` line 181) — never in motion code. `simulation.py:97-99` calls `vehicle.update()` for **all** vehicles each step with no `COMPLETED` check.

**Runtime confirmation:** in `data/simulation_scenario_1_20260612_140837.json`, every trajectory point of V1 lies on the inbound ray toward (500, 500); no vehicle's x/y ever passes the center in any data file.

**Root cause:** Every step, the heading is recomputed as
`direction = self._calculate_direction(self.position, config.INTERSECTION_CENTER)`.
The vehicle's `target_position` is never used for steering. A vehicle that reaches the center would have the direction vector flip every step and jitter in place; it can never travel *through* the intersection and out the other side. Vehicles in `COMPLETED` state are also still updated every step (the engine calls `update()` unconditionally, and no velocity branch handles `COMPLETED`), so even "finished" vehicles keep crawling back toward the center.

**Consequence:** Even with C1/C3/C4 fixed, no vehicle could exit the intersection or genuinely reach `COMPLETED` via forward travel.

**Proposed fix:** Steer toward `config.INTERSECTION_CENTER` while `APPROACHING`/`WAITING`, and toward `self.target_position` once `CROSSING`. Skip `update()` (or early-return) for `COMPLETED` vehicles.

---

### C3. Post-intersection target is computed on the wrong side of the intersection (and off-grid)

**File:** `simulation.py` — `initialize_scenario()` (lines 59–62)

**Evidence:**

```python
# simulation.py:59-62
target_point = (
    config.INTERSECTION_CENTER[0] + (spawn_point[0] - config.INTERSECTION_CENTER[0]) * 2,
    config.INTERSECTION_CENTER[1] + (spawn_point[1] - config.INTERSECTION_CENTER[1]) * 2,
)
```

Worked example: spawn (50, 500), center (500, 500) → target = 500 + (50−500)×2 = **(−400, 500)**. The "destination after crossing" is 450 px *behind* the spawn point and outside the 1000×1000 grid.

**Root cause:** The formula extends the spawn vector *away from the center on the same side as the spawn*. For spawn (50, 500) it yields (−400, 500) — 450 px behind the spawn point and outside the 1000×1000 grid. The intended "opposite side" point is the mirror image: `center − (spawn − center)`, e.g. (950, 500).

**Consequence:** The `CROSSING → COMPLETED` test in `vehicle._update_state()` compares distance traveled against `0.8 × distance(start, target)` — a number derived from a nonsense target. With current geometry it happens to roughly cancel out (450 px), which *masks* the bug; with asymmetric spawns it would not. Combined with C2, completion is unreachable anyway.

**Proposed fix:** `target_point = (2*center_x − spawn_x, 2*center_y − spawn_y)`, then base completion on having passed the intersection along the travel axis (or distance-past-center), not on a percentage heuristic.

---

### C4. WAITING is an inescapable trap: stopped vehicles are excluded from RSU decisions forever

**Files:** `vehicle.py` — `update()` WAITING branch (lines 113–126), `_update_state()` (lines 164–202), `_calculate_eta()` (lines 239–244); `rsu.py` — `make_priority_decision()` line 96

**Evidence:**

```python
# vehicle.py:239-244 — stopped vehicle reports infinite ETA
def _calculate_eta(self) -> float:
    distance = self._distance_to_intersection()
    if self.current_velocity > 0:
        return distance / self.current_velocity
    return float('inf')

# rsu.py:93-97 — infinite ETA = permanently excluded from FCFS decisions
unprocessed = [
    (entry.arrival_time, vehicle_id)
    for vehicle_id, entry in self.active_vehicles.items()
    if not entry.processed and entry.eta_to_intersection < float('inf')
]

# vehicle.py:123-126 — WAITING without priority: brake to a dead stop
else:
    if collision_risk > 0.6:
        self.current_velocity = 0
    else:
        self.current_velocity = max(0, self.current_velocity - config.VEHICLE_DECELERATION * 2)
```

**Runtime confirmation (latest run, `..._140837.json`):** V1 stops at (391.3, 500) and V2 at (610.9, 500) — both ~110 px from center, between the 120 px WAITING trigger and the 80 px escape hatch; `total_wait_time = 180.4 s`; RSU made only 16 decisions in 1000 steps (decisions cease the moment vehicles stop and ETAs go infinite); `rsu_statistics.active_vehicles = 2` at end of run (nothing ever released).

**Root cause chain:**

1. A vehicle enters `WAITING` when it gets within `INTERSECTION_SIZE * 1.2 = 120` px without `can_cross` (which, per C1, is always the case).
2. In `WAITING` without priority it brakes at `VEHICLE_DECELERATION * 2 = 4` px/s **per step** (a units bug — see M6: 10× the configured rate), reaching velocity 0 within ~8 steps, ~10 px of travel. It stops at ~110 px out — short of the 80 px "cross anyway" escape hatch in `_update_state()` (line 199), which is therefore unreachable.
3. With velocity 0, `_calculate_eta()` returns `inf`.
4. `rsu.make_priority_decision()` filters candidates with `entry.eta_to_intersection < float('inf')` — so a stopped vehicle is **invisible to the RSU** and can never be (re)assigned priority. This matches the data: only 16 decisions in 1000 steps; decisions cease once vehicles stop.
5. Meanwhile the first vehicle stays in `current_crossing_vehicles` forever (it never completes, and `remove_completed_vehicle()` is only called on completion), so `vehicles_crossing_now` is permanently 1 and nobody else could be granted priority anyway.

**Consequence:** Permanent system-wide deadlock ~110 px from the intersection. This is exactly what every data file shows.

**Proposed fix:** (a) Don't exclude stopped vehicles from FCFS — a queued, stopped vehicle is the *most* eligible, not ineligible; use distance or queue presence instead of finite ETA. (b) Implement the `FCFS_TIMEOUT` already defined in `config.py` to reclaim the crossing slot from a stalled grant-holder. (c) Re-send priority grants until acknowledged or crossing observed.

---

### C5. V2V messages are received but never used — there is no V2V negotiation

**Files:** `vehicle.py` — `receive_message()` (lines 246–254); `simulation.py` — Step 3B (lines 125–136)

**Evidence:**

```python
# vehicle.py:246-254 — the ONLY message handling a vehicle has;
# 'v2v_info' messages are stored and never read again
def receive_message(self, message: Dict, current_time: float) -> None:
    message['received_at'] = current_time
    self.received_messages.append(message)
    if message.get('type') == 'priority_assignment':   # 'v2v_info' falls through
        self.priority = message.get('priority')
        self.can_cross = (self.priority == 1)

# simulation.py:209-225 — braking decisions use OMNISCIENT engine access
# to other vehicles' true state, bypassing the communication layer entirely
for other_vehicle in self.vehicles.values():
    ...
    other_info = other_vehicle.get_vehicle_info(self.current_time)
    risk = self.collision_analyzer.predictor.calculate_collision_risk(...)
```

**Runtime confirmation:** data files from 10:24–10:45 show `v2v.total_messages_sent = 0` (older `simulation.py` never called the module); files from 10:52 onward show ~1,760–1,769 sent — with identical vehicle behavior and identical `successful_crossings = 0`, proving the V2V traffic has zero behavioral effect.

**Root cause:** The engine wraps incoming V2V payloads as `{'type': 'v2v_info', ...}` and calls `vehicle.receive_message()`. That method only has handling for `type == 'priority_assignment'`; `'v2v_info'` messages are appended to `received_messages` and ignored. No vehicle behavior (speed, yielding, gap acceptance, negotiation) ever reads another vehicle's broadcast state. Collision risk used for braking is computed *omnisciently* by the engine (`_calculate_vehicle_collision_risk()` reads other vehicles' true state directly), bypassing the communication layer entirely.

Note: the reported test finding "V2V Messages Sent = 0" is from **older runs** (data files timestamped ≤ 10:45 show 0/0; runs from 10:54 onward show ~1,769 sent). The current code does broadcast — but the content is dead on arrival.

**Consequence:** The system's titular feature — V2V *negotiation* — does not exist. The simulation is purely centralized (RSU/V2I), and even that is broken per C1. The V2V layer only inflates message statistics.

**Proposed fix:** Implement an actual consumer: vehicles maintain a neighbor table from `v2v_info` messages and use it for distributed collision risk (replacing the engine's omniscient calculation) and/or a fallback negotiation protocol (e.g., ETA-based yielding) when RSU is silent. Define and use the unused `COLLISION_WARNING` / `TRAJECTORY_CORRECTION` message types or remove them.

---

### C6. Per-vehicle message retrieval destroys other vehicles' V2V mail

**File:** `communication.py` — `V2VCommunication.get_received_messages()` (lines 168–171); same pattern in `V2ICommunication.get_vehicle_messages()` (lines 226–229)

**Evidence:**

```python
# communication.py:168-171 — drains the SHARED queue, keeps only this
# vehicle's mail, silently discards everyone else's
def get_received_messages(self, vehicle_id: str, current_time: float) -> List[Message]:
    messages = self.channel.get_pending_messages(current_time)   # destructive
    return [msg for msg in messages if msg.receiver_id == vehicle_id]
```

In `simulation.py:126-130` this is called per vehicle in a loop; dict insertion order means V1 always drains the queue first, so later vehicles receive almost nothing.

**Root cause:** Identical design flaw to C1, on the V2V side. `get_received_messages(vehicle_id)` drains *all* delivered messages from the shared channel, returns the ones addressed to `vehicle_id`, and **discards the rest**. In the engine's Step 3B loop, the first vehicle iterated (V1, by dict insertion order) drains the queue; every later vehicle receives almost nothing. The channel's `received_messages` statistic counts the drained-and-discarded messages as "received," so the reported V2V received count (~1,767) wildly overstates actual delivery.

**Consequence:** Even after fixing C5, V2V delivery would be biased to one vehicle and the statistics would remain wrong.

**Proposed fix:** Same as C1 — per-receiver filtering inside the channel; only dequeue messages addressed to the requester.

---

## MEDIUM FINDINGS

### M1. FCFS ordering is not first-come-first-served

**Files:** `rsu.py` — `register_vehicle()` (lines 57–71), `make_priority_decision()` (lines 92–99); `simulation.py` — `initialize_scenario()` line 85

**Root cause:** All vehicles are registered at simulation init with `current_time = 0`, so every `VehicleEntry.arrival_time` is 0. The FCFS sort `unprocessed.sort()` therefore ties on arrival time and orders by vehicle ID string — priority is effectively alphabetical, not temporal. `arrival_time` should be the time the vehicle *enters the intersection approach zone* (or RSU range), recorded when first detected, not at registration. The separate `priority_queue` field that was presumably meant for this is never used (see Minor N1).

**Proposed fix:** Record arrival when a vehicle first comes within a defined approach radius; re-register or timestamp on that event.

### M2. Collision detection physics is wrong in `RSU.detect_collision_risk()`

**File:** `rsu.py` — `detect_collision_risk()` (lines 135–169)

**Root causes:**
- `relative_velocity = v1['velocity'] - v2['velocity']` subtracts scalar *speeds*. The result's sign depends on argument order and says nothing about whether vehicles are closing. Two vehicles converging head-on at equal speed give 0 → "no risk." The correct quantity is the closing speed: the dot product of relative velocity *vector* with the unit vector between positions.
- The check only fires when `distance < COLLISION_THRESHOLD` (30 px). With 20 px vehicles, 30 px separation is already a near-collision — this detects collisions, it doesn't *predict* them. No use of ETA/trajectory data despite the RSU having it.

**Consequence:** `collision_detections = 0` in all runs even in scenario_2 (4 vehicles). The RSU's "collision detection" feature is non-functional in practice.

**Proposed fix:** Use vector closing speed and a time-to-conflict estimate (both vehicles' ETA to the conflict zone overlapping within a margin), not instantaneous proximity.

### M3. `successful_crossings` is counted incorrectly (multi-count + dead guard)

**File:** `simulation.py` — `step()` Step 9 (lines 196–201), `_record_step_metrics()` (lines 227–234)

**Evidence:**

```python
# simulation.py:196-201 — fires EVERY step for a completed vehicle;
# the inner if is a tautology, nothing marks "already counted"
for vehicle in self.vehicles.values():
    if vehicle.state == VehicleState.COMPLETED and vehicle.crossing_completed:
        self.rsu.remove_completed_vehicle(vehicle.vehicle_id)
        if vehicle.state == VehicleState.COMPLETED:
            self.performance_metrics['successful_crossings'] += 1

# vehicle.py:183-184 — vehicle sets crossing_completed itself on transition,
# which permanently disables the once-only guard in _record_step_metrics()
self.state = VehicleState.COMPLETED
self.crossing_completed = True
```

**Root cause:** Two independent counters fight each other:
- Step 9 increments `successful_crossings` for every vehicle with `state == COMPLETED and crossing_completed` — **every step, forever**, with no once-only guard (the inner `if vehicle.state == VehicleState.COMPLETED` is a tautology). One completed vehicle surviving 500 steps would count as ~500 crossings.
- `_record_step_metrics()` has a once-only guard (`and not vehicle.crossing_completed`), but it can never fire because `vehicle._update_state()` sets `crossing_completed = True` itself at the moment of completion (vehicle.py lines 184, 189).

Currently masked because nothing ever completes (C1–C4); the moment those are fixed, this metric explodes.

**Proposed fix:** Count completion exactly once, at the state transition (e.g., in `_update_state` raise an event/flag the engine consumes once), and delete one of the two counting sites.

### M4. `Vehicle.receive_message()` priority handling is dead code (key mismatch)

**File:** `vehicle.py` — `receive_message()` (lines 252–254); `simulation.py` — Step 7 line 183

**Root cause:** The handler checks `message.get('type') == 'priority_assignment'`, but V2I messages forwarded via `msg.to_dict()` carry the key **`message_type`** (see `Message.to_dict()`, communication.py line 35–39), and V2V wrappers use `type: 'v2v_info'`. No message ever matches. The engine compensates by mutating `vehicle.priority` / `vehicle.can_cross` directly in Step 7 (lines 178–180) — duplicated, divergent logic.

**Proposed fix:** Pick one owner for message handling (the vehicle), fix the key, and remove the engine's direct mutation.

### M5. `arrival_times` scenario parameter works backwards

**File:** `simulation.py` — `initialize_scenario()` (lines 73–80)

**Root cause:** To simulate a *later* arrival, the code moves the spawn point **toward** the intersection (`spawn − (spawn − center)/100 × offset`), making the vehicle arrive *earlier*. A vehicle meant to arrive 2 s later starts 180 px closer. The semantics are inverted; also, vehicles should arguably spawn over time rather than be pre-placed.

**Proposed fix:** Either move the spawn *away* from the center by `arrival_time × speed`, or implement actual deferred spawning at `t = arrival_time`.

### M6. Acceleration/deceleration ignore the time step (10× the configured rates)

**File:** `vehicle.py` — `update()` (lines 93–133); `config.py` — `VEHICLE_DECELERATION`

**Evidence:**

```python
# config.py:19,24
VEHICLE_DECELERATION = 2   # pixels per second^2
TIME_STEP_DURATION = 0.1   # seconds per step

# vehicle.py:97-98 — subtracted per STEP, not per second:
# 6 px/s lost per 0.1 s step = 60 px/s², i.e. 10x the configured 6 px/s²
decel_rate = config.VEHICLE_DECELERATION * 3.0
self.current_velocity = max(0, self.current_velocity - decel_rate)
```

Contrast with `_update_position()` (vehicle.py:147), which *does* multiply by `TIME_STEP_DURATION` — velocity integration and acceleration integration use inconsistent time bases.

**Root cause:** `VEHICLE_DECELERATION` is documented as px/s², but it's applied per *step* without multiplying by `TIME_STEP_DURATION` (0.1 s): `self.current_velocity - decel_rate`. Effective deceleration is 10× the configured value; the hardcoded acceleration constants (`+1.0`, `+1.5`, `+3.0` per step = 10–30 px/s²) have the same issue. This is why vehicles slam to a halt within ~10 px in WAITING (feeds C4).

**Proposed fix:** `velocity += a × TIME_STEP_DURATION` everywhere; move the magic acceleration constants into `config.py`.

### M7. Communication loss statistics don't measure loss

**File:** `communication.py` — `CommunicationChannel.send_message()` (lines 57–84), `get_statistics()` (lines 101–113)

**Root cause:** Messages dropped by the range check or the 2% random loss are **not** appended to `sent_messages` — they vanish before being counted. `received_messages` counts everything drained from the queue (including messages discarded by the C1/C6 filters). The reported "loss rate" (~0.1%) is therefore just the residual in-flight queue, not the simulated 2% loss. The per-receiver success dict returned by `broadcast_vehicle_info()` is discarded by the caller.

**Proposed fix:** Count attempts, deliveries, range-drops, and random-drops separately; compute loss = drops/attempts.

### M8. `CollisionAnalyzer` is never used — collision analysis output is always empty

**Files:** `ai_predictor.py` — `CollisionAnalyzer.analyze_vehicle_pair()` (line 208), `detect_head_on_collision()` (line 133); `simulation.py` — line 219

**Root cause:** The engine instantiates `CollisionAnalyzer` but only ever calls `collision_analyzer.predictor.calculate_collision_risk()` — reaching through to the inner predictor. `analyze_vehicle_pair()` (which populates `collision_events`, head-on detection, time-to-collision) is never invoked. Hence `collision_analysis.total_high_risk_events = 0` always, and `collision_risk.png` always renders "No collision events detected."

**Proposed fix:** Call `analyze_vehicle_pair()` from the engine's Step 8 (replacing the redundant per-pair `rsu.detect_collision_risk([v_a, v_b])` call — passing exactly 2 vehicles into a function that itself loops over pairs).

### M9. Trajectory prediction's "AI" features are inert

**File:** `ai_predictor.py` — `predict_trajectory()` (lines 36–75), `calculate_collision_risk()` (lines 94–108)

**Root causes:**
- `calculate_collision_risk()` predicts under synthetic IDs (`f"{id}_pred"`) that never receive history via `update_vehicle_history()` (which stores under the real ID). The exponential-smoothing branch therefore never executes in the risk path — predictions are plain constant-velocity extrapolation.
- Even when the smoothing branch runs, `_exponential_smooth()` recomputes the same scalar from full history on every loop iteration, so all `steps_ahead` positions use one constant velocity — the loop adds nothing.
- `config.PREDICTION_WINDOW` exists but call sites use the hardcoded default `10`.
- Direction is assumed constant (toward the intersection), so predictions through turns/exits would be wrong once C2 is fixed.

**Proposed fix:** Use real vehicle IDs for history lookup, smooth once before the loop (or model deceleration per-step), read `PREDICTION_WINDOW` from config. Be honest in docs that this is physics extrapolation, not ML.

### M10. Repository is not GitHub-ready

**Files:** repo root

**Issues:**
- **No `.gitignore`**, and the index already stages: `__pycache__/*.pyc` (7 files), 16 generated `data/*.json` runs, generated `outputs/*.png`, and `Final report Updated.docx` (a 'binary report with spaces in the filename — likely not meant for a public repo).
- **No commits yet** — the branch `main` has no history; everything is staged only.
- **No LICENSE** file.
- **No tests**, though `README.md` advertises a `tests/` directory; `docs/` is also advertised but doesn't exist.
- `requirements.txt` pins `python-docx`, which no source file imports.
- Documentation overclaims: `README.md` advertises "Emergency Vehicle Support" (not implemented — `rsu.make_priority_decision()` never reads `vehicle_type`, despite `scenario_3` configuring it), "Real-time Collision Avoidance," and "AI-powered" prediction (see M2, M8, M9). `PROJECT_COMPLETION_SUMMARY.md` and the previous `AUDIT_REPORT.md` directly contradict each other about what works.

**Proposed fix:** Add `.gitignore` (`__pycache__/`, `*.pyc`, `data/`, `outputs/`), `git rm --cached` the generated/binary files, add a LICENSE, align README claims with reality (or implement the claims), remove the unused dependency, and make an initial commit only after that cleanup.

---

## MINOR FINDINGS

### N1. Dead code and unused definitions

| Location | Item | Note |
|---|---|---|
| `rsu.py:45` | `priority_queue` | declared, never read/written |
| `rsu.py:171` | `get_vehicle_priority()` | never called |
| `rsu.py:213` | `get_detailed_decisions()` | never called |
| `rsu.py:217` | `get_collision_risk_summary()` | never called (RSU collision stats unreported) |
| `rsu.py:14` | `RSUState.IDLE/PROCESSING` | state set but never read; `PROCESSING` never assigned |
| `vehicle.py:23` | `VehicleStatus` dataclass + `get_status()` | never called |
| `vehicle.py:273` | `reset_communication_flags()`, `last_v2v_update`, `last_v2i_update` | never called/read |
| `vehicle.py:16` | `VehicleState.IDLE` | never assigned |
| `ai_predictor.py:147` | `estimate_crossing_time()` | never called |
| `ai_predictor.py:155` | `calculate_trajectory_divergence()` | never called |
| `ai_predictor.py:192` | `TrajectoryPredictor.get_statistics()` | never called |
| `communication.py:15` | `MessageType.COLLISION_WARNING`, `TRAJECTORY_CORRECTION`, `ACK` | never sent |
| `communication.py:32` | `Message.sequence_number` (always 0), `Message.priority` | never used |
| `config.py` | `PREDICTION_WINDOW`, `FCFS_TIMEOUT`, `VEHICLE_SPEED_MIN/MAX`, `FPS`, `DEBUG_MODE`, `SAVE_SIMULATION_DATA`, `VEHICLE_SIZE` | defined, never read |
| `simulation.py:38` | `simulation_log` | initialized, never written |
| `simulation.py:43` | `performance_metrics['communication_delays']` | never populated (always `[]`) |
| `visualizer.py:8` | `FuncAnimation` import | unused (no animation implemented) |

### N2. Leftover debug prints in production path

`simulation.py` lines 182 and 185 print `DEBUG: ...` unconditionally (not gated on `args.debug` / `config.DEBUG_MODE`). They currently never fire only because of bug C1.

### N3. Broken CLI flags in `main.py`

`--visualize` and `--save` use `action='store_true'` with `default=True` — passing the flag is a no-op and there is no way to turn either off. `--time-steps` is parsed and printed but **never passed to the engine** (`SimulationEngine` reads `config.SIMULATION_TIME_STEPS` directly), so the option silently does nothing.

### N4. `state_history` bloat

`vehicle.py:172` — inside the `APPROACHING` branch, `state_history.append(...)` runs every step (it's outside the inner transition `if`), recording hundreds of duplicate entries instead of transitions only.

### N5. Unbounded memory growth

`vehicle.received_messages` accrues every message forever (~thousands per run, with full payload dicts). `trajectory`/`velocity_history` also grow per step (acceptable at 1,000 steps, but unbounded by design).

### N6. Unit confusion: meters vs pixels

`config.py` documents `V2V_RANGE`/`V2I_RANGE` in **meters** and vehicle speeds in **pixels**/s; distances passed to the channel are in pixels. The simulation works only because both are treated as the same unit. Document a single world unit (or a px↔m scale factor).

### N7. `_make_serializable` doesn't do what its comment says

`simulation.py:296` — comment says "Convert numpy types" but no numpy handling exists (works today only because no numpy scalars reach results); `inf` becomes the string `"Infinity"` (asymmetric typing for consumers); `NaN` is unhandled.

### N8. `visualizer.py` hard-caps at 4 vehicles

`plot_velocity_profile()` and `plot_predicted_vs_actual_trajectory()` use fixed 2×2 grids and silently skip vehicles beyond the 4th. Fine for current scenarios; will silently drop data for larger ones. Also, the "Predicted Path" in `predicted_vs_actual.png` is recomputed inside the visualizer from raw trajectory points — it is **not** the `TrajectoryPredictor`'s output, so the plot doesn't validate the actual predictor (compounds M9).

### N9. Duplicate distance helpers

Euclidean distance is independently implemented in `vehicle.py`, `rsu.py`, `ai_predictor.py`, and twice in `communication.py`. Harmless but should live in one utility module.

---

## Root-Cause Summary: "Why do vehicles never complete crossing?"

```
RSU sends PRIORITY_ASSIGNMENT ──► shared V2I queue
        │
        ▼
[C1] get_rsu_messages() drains the queue first and drops the
     priority payloads (no 'vehicle_id' key) ──► vehicles never
     get can_cross = True
        │
        ▼
Vehicle reaches 120 px ──► state = WAITING (no priority)
        │
        ▼
[M6] brakes at 10× configured rate ──► stops at ~110 px,
     short of the 80 px escape hatch
        │
        ▼
[C4] velocity 0 ──► ETA = inf ──► filtered out of every future
     RSU decision; grant-holder never releases the slot
        │
        ▼
PERMANENT DEADLOCK  (and even if it crossed: [C2] it steers at the
center forever and [C3] its exit target is behind its spawn point)
```

## Root-Cause Summary: "Why was V2V Sent/Received = 0?"

Data files timestamped 10:24–10:45 were produced by an older `simulation.py` that never invoked `V2VCommunication`. The current code broadcasts every step (runs from 10:52 onward show ~1,769 sent). However: [C5] received V2V messages are never acted on, [C6] per-vehicle retrieval discards other vehicles' mail, and [M7] the statistics count drained-and-discarded messages as "received." V2V is presently telemetry theater — fixing the counters without fixing C5/C6 would only hide the problem.

---

## Recommended Fix Order

1. **C1 + C6** — per-receiver message delivery in `CommunicationChannel` (one fix covers both).
2. **C2 + C3** — correct target computation and state-dependent steering; redefine completion.
3. **C4 + M6** — time-step-scaled dynamics; FCFS eligibility independent of ETA; implement `FCFS_TIMEOUT`.
4. **M3 / M4 / M1 / M5** — metrics correctness, message handling ownership, true FCFS arrival times, arrival-time semantics.
5. **C5** — implement actual V2V usage (neighbor table → distributed risk / negotiation fallback); replace the engine's omniscient risk calculation.
6. **M2 / M8 / M9** — real collision prediction and analyzer wiring.
7. **M10 + Minors** — `.gitignore`, untrack generated/binary files, LICENSE, docs honesty, dead-code removal, CLI fixes, debug-print removal.

*No fixes have been implemented; this document is analysis only.*
