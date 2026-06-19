"""
Smart EV Charging System — MQTT Telemetry Simulator
Publishes synthetic charging session data to a local MQTT broker.
Use this to test the dashboard without physical hardware.

Usage:
    pip install paho-mqtt
    python mqtt_simulator.py [--broker 127.0.0.1] [--port 1883]
"""
from __future__ import annotations

import argparse
import json
import random
import time

import paho.mqtt.client as mqtt

TOPIC_TELEMETRY = "ev/telemetry"
TOPIC_SESSION   = "ev/session"
TOPIC_FAULT     = "ev/fault"

SIM_UID          = "SIMTEST1"
PUBLISH_INTERVAL = 5          # seconds — matches firmware MQTT_PUBLISH_INTERVAL_MS
SESSION_DURATION = 300        # seconds to simulate a full charge (60% → 100%)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="EV Charger MQTT simulator")
    p.add_argument("--broker", default="127.0.0.1")
    p.add_argument("--port",   default=1883, type=int)
    p.add_argument("--rate",   default=8.0,  type=float, help="₹/kWh tariff rate")
    return p.parse_args()


def build_telemetry(elapsed: int, rate: float) -> dict:
    progress = min(elapsed / SESSION_DURATION, 1.0)
    soc       = 60.0 + progress * 40.0                          # 60% → 100%
    voltage   = 11.50 + progress * 1.10                         # 11.5V → 12.6V
    current   = 0.85 + random.uniform(-0.02, 0.02)
    power_w   = voltage * current
    energy_wh = power_w * (elapsed / 3600.0)
    temp_c    = 28.0 + progress * 4.0 + random.uniform(-0.3, 0.3)

    return {
        "uid":       SIM_UID,
        "voltage":   round(voltage,   2),
        "current":   round(current,   3),
        "power_w":   round(power_w,   2),
        "energy_wh": round(energy_wh, 3),
        "soc":       round(soc,        1),
        "temp_c":    round(temp_c,     1),
        "elapsed_s": elapsed,
    }


def main() -> None:
    args   = parse_args()
    client = mqtt.Client(client_id="ev_simulator")
    client.connect(args.broker, args.port, keepalive=60)
    client.loop_start()

    print(f"[SIM] Connected to {args.broker}:{args.port}")
    print(f"[SIM] Publishing session for UID={SIM_UID} (Ctrl+C to stop)")

    # Announce session start
    client.publish(TOPIC_SESSION, json.dumps({
        "event": "session_start",
        "uid":   SIM_UID,
    }))
    print("[SIM] → session_start published")

    start = time.time()
    try:
        while True:
            elapsed = int(time.time() - start)
            data    = build_telemetry(elapsed, args.rate)

            client.publish(TOPIC_TELEMETRY, json.dumps(data))
            print(
                f"[SIM] t={elapsed:4d}s  SOC={data['soc']:5.1f}%  "
                f"V={data['voltage']:.2f}V  I={data['current']:.3f}A  "
                f"T={data['temp_c']:.1f}°C  E={data['energy_wh']:.3f}Wh"
            )

            if data["soc"] >= 100.0:
                cost_rs = (data["energy_wh"] / 1000.0) * args.rate
                client.publish(TOPIC_SESSION, json.dumps({
                    "event":      "session_end",
                    "uid":        SIM_UID,
                    "energy_wh":  data["energy_wh"],
                    "cost_rs":    round(cost_rs, 2),
                    "duration_s": elapsed,
                }))
                print(f"[SIM] → session_end  energy={data['energy_wh']:.2f}Wh  cost=₹{cost_rs:.2f}")
                break

            time.sleep(PUBLISH_INTERVAL)

    except KeyboardInterrupt:
        print("\n[SIM] Interrupted — publishing fault event")
        client.publish(TOPIC_FAULT, json.dumps({
            "event":  "fault",
            "uid":    SIM_UID,
            "reason": "SIM_INTERRUPT",
        }))

    finally:
        client.loop_stop()
        client.disconnect()
        print("[SIM] Disconnected")


if __name__ == "__main__":
    main()
