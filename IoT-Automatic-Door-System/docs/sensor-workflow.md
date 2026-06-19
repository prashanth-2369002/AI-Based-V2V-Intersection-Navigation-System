# Sensor Workflow

## Detection Pipeline

The system uses a three-stage detection pipeline that progressively commits resources. Each stage gates the next, reducing false positives and conserving power.

```
Stage 1: PIR (Low power, coarse)
  └── Stage 2: Ultrasonic (Medium power, range-accurate)
        └── Stage 3: RFID / Proximity (Targeted, identity-aware)
```

## Stage 1 — PIR Motion Detection

**Sensor:** HC-SR501 Passive Infrared  
**Principle:** Detects change in IR radiation from warm bodies crossing sensor's Fresnel zones

```
Idle state: GPIO 13 = LOW
Motion:     GPIO 13 = HIGH for 3–300 s (adjustable via trimpot)
```

**Filtering applied:**
- 2-second cooldown after each trigger (prevents rapid re-trigger)
- PIR warmup period of 2 s at boot (sensor calibrates to ambient IR)
- Only `RISING` edge is acted upon

**When PIR fires → proceed to Stage 2**

---

## Stage 2 — Ultrasonic Distance Measurement

**Sensor:** HC-SR04  
**Principle:** Time-of-flight — measures echo return time from 40 kHz sound burst

```
Distance (cm) = pulse_duration_µs / 58
```

**Three-sample rolling average** removes multipath reflections.

| Distance | Action |
|----------|--------|
| < 0 (timeout) | Abort — possible sensor fault |
| 0–30 cm | Proximity unlock zone (no RFID needed) |
| 31–100 cm | RFID authentication required |
| > 100 cm | Out of trigger zone — ignore |

**During door swing (safety mode):**
- Sensor polled every 50 ms
- If distance < 10 cm → stop servo immediately
- Hold door open; reset auto-close timer

---

## Stage 3 — RFID / Proximity Decision

**If RFID card presented:**

```
1. rfid.PICC_IsNewCardPresent()  → card in field?
2. rfid.PICC_ReadCardSerial()    → read 4-byte UID
3. UID → uppercase hex string    e.g. "A1B2C3D4"
4. Linear search in AUTHORIZED_UIDS[]
5. Match  → ACCESS_GRANTED + openDoor("rfid")
   No match → ACCESS_DENIED + buzzer(3) + red LED
```

**If no RFID card and distance ≤ 30 cm:**

```
→ ACCESS_GRANTED (proximity mode) + openDoor("proximity")
   [Used for guests or hands-free entry]
```

---

## Auto-Close Logic

```
doorOpenedAt = millis()          // set when door reaches 90°

Loop every 100 ms:
  if (millis() - doorOpenedAt > AUTO_CLOSE_MS):
    dist = ultrasonicRead()
    if (dist > OBSTACLE_THRESHOLD or dist < 0):
      closeDoor()
    else:
      doorOpenedAt = millis()    // reset: obstacle present, keep open
      Serial.println("SAFETY: holding door")
```

---

## MQTT Event Schema

Every access event is published to `door/event` as JSON:

```json
{
  "event":     "ACCESS_GRANTED",
  "uid":       "A1B2C3D4",
  "reason":    "rfid",
  "uptime_ms": 123456
}
```

**Event types:**

| Event | Trigger |
|-------|---------|
| `ACCESS_GRANTED` | Valid RFID or proximity |
| `ACCESS_DENIED` | Unknown RFID UID |
| `DOOR_OPENED` | Door servo reached open position |
| `DOOR_CLOSED` | Door servo reached closed position |
| `SAFETY_HALT` | Obstacle detected during swing |
| `REMOTE_OPEN` | `door/command OPEN` received |
| `REMOTE_CLOSE` | `door/command CLOSE` received |

---

## Timing Diagram

```
Time →

PIR:        ──────▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄────────────────────────
                   ↑ motion in
Ultrasonic: ────────────▲────────────────────────────────────────
                         45 cm → in range
RFID scan:  ──────────────────▲──────────────────────────────────
                               UID match
Door servo: ────────────────────────▄▄▄▄▄▄▄▄▄▄▄▄▄▄────▄▄▄▄▄▄──
                                    opening ↗   open    closing ↘
MQTT:       ────────────────────────────────▲───────────────▲───
                                            GRANTED         CLOSED
LCD:        [Scanning...]  [Welcome!  ]  [Door Open... ]  [Locked]
LED Green:  ████████████████████████████████████████████████████
LED Red:    ─────────────────────────────────────────────────────
```
