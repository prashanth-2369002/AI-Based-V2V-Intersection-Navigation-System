# Schematics

This folder contains circuit schematic files for the Smart EV Charging System.

## Files

| File | Format | Description |
|---|---|---|
| `schematic.pdf` | PDF | Full circuit schematic (printable, A3) |
| `schematic.fzz` | Fritzing | Editable Fritzing project |

> **Note:** The schematic files are not included in the initial repository commit because they are binary files. Add them here after exporting from your EDA tool.

---

## How to Create the Schematic

The recommended free tools for students:

### Fritzing (Beginner-friendly)

1. Download from [fritzing.org](https://fritzing.org/)
2. Use the **Breadboard view** to lay out your circuit visually
3. Switch to **Schematic view** for the professional schematic
4. Export as PDF: `File → Export → PDF`

### EasyEDA (Browser-based, no install)

1. Go to [easyeda.com](https://easyeda.com)
2. Search for each component in the library (ESP32, MFRC522, INA219, DS18B20, relay)
3. Draw connections per the pin mapping in `docs/hardware-requirements.md`
4. Export as PDF or PNG

---

## Schematic Sub-circuits

The complete schematic consists of these interconnected sub-circuits:

```
┌──────────────────────────────────────────────────────────────────┐
│                         SYSTEM SCHEMATIC                         │
│                                                                  │
│  ┌─────────┐   SPI    ┌──────────┐                              │
│  │  ESP32  │◄────────►│ MFRC522  │  (3.3V)                     │
│  │         │   I2C    ├──────────┤                              │
│  │         │◄────────►│  INA219  │◄── V+I measurement line      │
│  │         │   I2C    ├──────────┤                              │
│  │         │◄────────►│LCD 20×4  │  (5V via PCF8574)           │
│  │         │  1-Wire  ├──────────┤                              │
│  │         │◄────────►│ DS18B20  │×2 + 4.7kΩ pull-up           │
│  │         │  GPIO    ├──────────┤                              │
│  │         │─────────►│  Relay   │──► Charging circuit          │
│  │         │  GPIO    ├──────────┤                              │
│  │         │─────────►│  Buzzer  │                              │
│  │         │  GPIO    ├──────────┤                              │
│  │         │─────────►│  LEDs    │×2 (330Ω series resistors)    │
│  └─────────┘          └──────────┘                              │
│       │                                                          │
│     Wi-Fi ──► MQTT Broker ──► Flask Dashboard                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## Voltage Domains

| Domain | Voltage | Powered By | Modules |
|---|---|---|---|
| Logic (low-power) | 3.3V | ESP32 3.3V pin | MFRC522, INA219, DS18B20 |
| Logic (5V) | 5V | USB VBUS or ESP32 VIN | LCD, Relay, Buzzer |
| Battery Pack | ~11.1V nominal | 18650 cells | Charging demonstration circuit |

**Never connect a 5V signal directly to an ESP32 GPIO.** The ESP32 is 3.3V logic. The peripherals on the 5V rail (LCD, Relay, Buzzer) are driven through the 3.3V GPIO but tolerate 3.3V logic signals as their input. Verify the datasheet of your specific relay and LCD module before connecting.
