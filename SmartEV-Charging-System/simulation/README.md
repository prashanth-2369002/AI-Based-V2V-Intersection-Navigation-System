# Simulation

This folder contains resources for simulating the Smart EV Charging System without physical hardware.

---

## Option 1 — Wokwi (Browser-based ESP32 Simulator)

[Wokwi](https://wokwi.com) is a free, browser-based simulator that supports the ESP32 and most peripherals used in this project.

### Supported Components

| Component | Wokwi Support |
|---|---|
| ESP32 DevKit v1 | Full support |
| MFRC522 RFID | Supported (virtual card tap via UI) |
| LCD 20×4 I2C | Supported |
| DS18B20 | Supported (temperature slider) |
| Relay Module | Simulated via LED |
| Buzzer | Simulated (audio output in browser) |
| INA219 | **Not available** — use the mock values below |

### Wokwi Diagram JSON

Copy this into `diagram.json` in your Wokwi project:

```json
{
  "version": 1,
  "author": "Smart EV Charging System",
  "editor": "wokwi",
  "parts": [
    { "type": "wokwi-esp32-devkit-v1", "id": "esp", "top": 0,    "left": 0,   "attrs": {} },
    { "type": "wokwi-lcd2004",          "id": "lcd", "top": -160, "left": 200, "attrs": { "pins": "i2c" } },
    { "type": "wokwi-led",              "id": "led1","top": 200,  "left": -60, "attrs": { "color": "green" } },
    { "type": "wokwi-led",              "id": "led2","top": 240,  "left": -60, "attrs": { "color": "red"   } },
    { "type": "wokwi-resistor",         "id": "r1",  "top": 200,  "left": -120,"attrs": { "value": "330" } },
    { "type": "wokwi-resistor",         "id": "r2",  "top": 240,  "left": -120,"attrs": { "value": "330" } }
  ],
  "connections": [
    ["esp:GND.1", "lcd:GND", "black", []],
    ["esp:5V",    "lcd:VCC", "red",   []],
    ["esp:21",    "lcd:SDA", "blue",  []],
    ["esp:22",    "lcd:SCL", "yellow",[]],
    ["esp:32",    "r1:1",    "green", []],
    ["r1:2",      "led1:A",  "green", []],
    ["led1:K",    "esp:GND.2","black",[]],
    ["esp:33",    "r2:1",    "red",   []],
    ["r2:2",      "led2:A",  "red",   []],
    ["led2:K",    "esp:GND.3","black",[]]
  ]
}
```

### INA219 Mock (for Wokwi)

Since Wokwi does not have an INA219 component, add this block at the top of `bms.cpp` when compiling for simulation:

```cpp
#ifdef WOKWI_SIMULATION
// Return synthetic values that ramp SOC from 60% → 100% over 5 minutes
BatteryData BMS::read() {
    BatteryData data = {};
    unsigned long elapsed = (millis() - _lastPollMs) / 1000UL;
    data.voltage     = 11.5 + (elapsed / 300.0f) * 1.1f;   // 11.5V → 12.6V
    data.current     = 0.85f;
    data.powerW      = data.voltage * data.current;
    data.temperature = 28.0f + (elapsed / 300.0f) * 4.0f;  // 28°C → 32°C
    data.ambientTemp = 25.0f;
    data.soc         = 60.0f + (elapsed / 300.0f) * 40.0f; // 60% → 100%
    data.soc         = min(data.soc, 100.0f);
    data.energyWh    = data.powerW * (elapsed / 3600.0f);
    data.isFault     = false;
    return data;
}
#endif
```

Add `-DWOKWI_SIMULATION` to Arduino build flags when targeting Wokwi.

---

## Option 2 — MQTT Simulator Script

If you want to test the **dashboard only** (without any ESP32 hardware or Wokwi), use the Python simulator script below. It publishes synthetic telemetry to the MQTT broker at the same rate as the real firmware.

### `simulation/mqtt_simulator.py`

```python
"""
Publishes synthetic EV charging telemetry to the MQTT broker.
Run this instead of real hardware to test the dashboard.
"""
import json
import time
import math
import random
import paho.mqtt.client as mqtt

BROKER = "127.0.0.1"
PORT   = 1883
UID    = "SIMTEST1"

client = mqtt.Client()
client.connect(BROKER, PORT, 60)
client.loop_start()

start = time.time()
print(f"[SIM] Publishing to {BROKER}:{PORT} — Ctrl+C to stop")

client.publish("ev/session", json.dumps({"event": "session_start", "uid": UID}))

try:
    while True:
        elapsed = int(time.time() - start)
        soc     = min(60.0 + (elapsed / 300.0) * 40.0, 100.0)
        voltage = 11.5 + (elapsed / 300.0) * 1.1
        current = 0.85 + random.uniform(-0.02, 0.02)
        power   = voltage * current
        temp    = 28.0 + (elapsed / 300.0) * 4.0 + random.uniform(-0.3, 0.3)
        energy  = power * (elapsed / 3600.0)

        payload = {
            "uid": UID, "voltage": round(voltage, 2),
            "current": round(current, 3), "power_w": round(power, 2),
            "energy_wh": round(energy, 3), "soc": round(soc, 1),
            "temp_c": round(temp, 1), "elapsed_s": elapsed,
        }
        client.publish("ev/telemetry", json.dumps(payload))
        print(f"[SIM] SOC={soc:.1f}%  V={voltage:.2f}V  T={temp:.1f}°C")

        if soc >= 100.0:
            cost = (energy / 1000.0) * 8.0
            client.publish("ev/session", json.dumps({
                "event": "session_end", "uid": UID,
                "energy_wh": round(energy, 2),
                "cost_rs": round(cost, 2),
                "duration_s": elapsed,
            }))
            print("[SIM] Battery full — session ended")
            break

        time.sleep(5)

except KeyboardInterrupt:
    print("[SIM] Stopped")

client.loop_stop()
client.disconnect()
```

### Running the Simulator

```bash
# 1. Start Mosquitto broker (see docs/software-requirements.md)
# 2. Start the Flask dashboard
cd software/dashboard && python app.py

# 3. In another terminal, run the simulator
cd simulation
pip install paho-mqtt
python mqtt_simulator.py

# 4. Open http://localhost:5000 in your browser
#    Dashboard will show live data from the simulator
```

---

## Option 3 — Proteus (Offline Simulation)

Proteus 8.x supports Arduino simulation but does not have native ESP32 support. If using a Proteus-compatible board (e.g., Arduino Uno) for demonstration, the firmware can be adapted by:

1. Replacing `WiFi.h` and `PubSubClient` with USB Serial output.
2. Replacing `EEPROM.h` with the AVR EEPROM library.
3. Removing the MQTT publish calls and printing JSON to Serial instead.

This is a significant code change and is not maintained in this repository. Wokwi is the recommended simulation path.
