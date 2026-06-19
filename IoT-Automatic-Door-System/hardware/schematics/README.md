# Hardware Schematics

## Files

| File | Description |
|------|-------------|
| `circuit_diagram.fzz` | Fritzing breadboard + schematic view |
| `circuit_diagram.pdf` | Exported PDF for printing |
| `pcb_layout.kicad_pcb` | KiCad PCB layout (future) |

> Place your exported Fritzing or KiCad files here.
> Export a PNG of the breadboard view and save as `circuit_diagram.png`
> for embedding in the README screenshots table.

## Quick Wiring Summary

```
ESP32 DevKit (38-pin)
│
├── GPIO 13  ──► HC-SR501 PIR OUT
├── GPIO 14  ──► HC-SR04  TRIG
├── GPIO 27  ──► HC-SR04  ECHO  (via 1kΩ/2kΩ divider)
│
├── GPIO 5   ──► RC522 SDA (CS)
├── GPIO 18  ──► RC522 SCK
├── GPIO 23  ──► RC522 MOSI
├── GPIO 19  ──► RC522 MISO
├── GPIO 22  ──► RC522 RST  /  LCD SCL
├── GPIO 21  ──► LCD SDA
│
├── GPIO 25  ──► MG996R Servo signal (orange wire)
├── GPIO 26  ──► Relay IN
├── GPIO 32  ──► Buzzer (+) via 100Ω
├── GPIO 33  ──► LED Red anode via 220Ω
├── GPIO 34  ──► LED Green anode via 220Ω
├── GPIO 4   ──► Button IN (10kΩ pullup to 3.3V)
└── GPIO 35  ──► Button OUT (10kΩ pullup to 3.3V)

Power Rails
├── 3.3V ──► RC522 VCC, HC-SR501 VCC (with 3.3V variant)
├── 5V   ──► HC-SR04 VCC, LCD VCC, Relay VCC, Buzzer VCC
├── EXT 5V ──► MG996R Red wire (separate supply, avoid ESP32 5V pin)
└── GND  ──► All components common ground
```

## Voltage Level Notes

The HC-SR04 ECHO pin outputs 5 V logic. The ESP32 GPIO is 3.3 V tolerant only.
Use a simple resistor divider before connecting:

```
ECHO ──[1kΩ]──┬── GPIO27
              [2kΩ]
               │
              GND
```

This drops 5 V → ~3.33 V safely.
