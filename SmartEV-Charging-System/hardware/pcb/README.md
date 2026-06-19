# PCB Design (Future Scope)

This folder is reserved for PCB design files for a future custom board revision of the Smart EV Charging System.

## Current Status

The prototype uses a **breadboard layout**. A custom PCB is a planned improvement for Phase 2 of the project.

---

## Why a Custom PCB?

The breadboard prototype has these limitations that a PCB would address:

| Issue | Impact | PCB Solution |
|---|---|---|
| Loose jumper connections | Intermittent sensor readings | Soldered traces, no connector slop |
| Breadboard contact resistance | Voltage measurement error | Low-resistance copper traces |
| No mounting holes | Cannot fit in an enclosure | Standoff holes on PCB corners |
| Exposed high-voltage relay | Safety hazard | Relay isolated on separate PCB section with creepage distance |
| No ESD protection on RFID | Card reader can fail | TVS diode on SPI lines |

---

## Planned PCB Specifications

| Parameter | Specification |
|---|---|
| Board size | 100 × 80 mm |
| Layers | 2 (top copper + bottom copper) |
| Stackup | FR4, 1.6 mm, 1 oz copper |
| Connectors | Terminal blocks for battery and relay; JST-PH for sensors |
| ESP32 | Surface-mount via stamp-hole module (ESP32-WROOM-32) |
| INA219 | Onboard IC (SOT-23 / SOP-8), not a breakout module |
| Protection | Reverse polarity diode on VIN; 500 mA PTC fuse on battery line |

---

## EDA Tools

When ready to design the PCB:

- **KiCad 7** (free, open-source) — recommended; has ESP32 and INA219 footprints in default library
- **EasyEDA** (browser-based) — easier for beginners, exports Gerber files
- **Altium CircuitMaker** (free tier) — Altium ecosystem, industry-relevant for resumes

---

## Gerber Files

Gerber files (for PCB fabrication) will be placed in this folder once the PCB design is complete:

```
hardware/pcb/
├── gerbers/
│   ├── ev_charger-F_Cu.gbr        # Front copper layer
│   ├── ev_charger-B_Cu.gbr        # Back copper layer
│   ├── ev_charger-F_Mask.gbr      # Front solder mask
│   ├── ev_charger-B_Mask.gbr      # Back solder mask
│   ├── ev_charger-F_SilkS.gbr     # Front silkscreen
│   ├── ev_charger-Edge_Cuts.gbr   # Board outline
│   └── ev_charger.drl             # Drill file
└── ev_charger.kicad_pcb           # KiCad project file
```

Gerber files can be uploaded directly to **JLCPCB** or **PCBWay** for fabrication. A 5-board order of a 100×80 mm 2-layer board costs approximately ₹500–700 including shipping (as of 2025).
