# Hardware Requirements

## Bill of Materials (BOM)

All components listed are off-the-shelf modules available from common electronics distributors (Robocraze, Evelta, Amazon India, Mouser). Prices are approximate and in Indian Rupees (June 2025).

| # | Component | Part / Module | Qty | Approx. Cost (₹) | Purpose |
|---|---|---|---|---|---|
| 1 | Microcontroller | ESP32 DevKit v1 (38-pin) | 1 | 450 | Main controller — Wi-Fi, BT, dual-core 240 MHz |
| 2 | RFID Reader | MFRC522 (3.3V SPI, blue board) | 1 | 130 | User authentication via 13.56 MHz cards |
| 3 | RFID Cards/Fobs | ISO-14443A MIFARE Classic 1K | 4 | 60 (set) | Test user cards |
| 4 | Power Sensor | INA219 breakout (Adafruit or clone) | 1 | 220 | Voltage + current measurement, I2C |
| 5 | Temperature Sensor | DS18B20 waterproof probe, TO-92 | 2 | 120 (pair) | Cell temp + ambient temp, 1-Wire |
| 6 | Current Sensor | ACS712-5A module | 1 | 120 | High-side current sense (backup / overcurrent) |
| 7 | Relay Module | 5V single-channel relay, opto-isolated | 1 | 80 | Charging circuit on/off switch |
| 8 | LCD Display | 20×4 character LCD with I2C backpack (PCF8574) | 1 | 250 | Live status display |
| 9 | Buzzer | 5V active buzzer module | 1 | 30 | Audio alerts |
| 10 | LEDs | 5mm green + red LED (with 330Ω resistors) | 2 | 20 | Status indicators |
| 11 | Charging Module | TP4056 with DW01A protection (micro-USB) | 1 | 60 | Bench-level Li-ion charging demo |
| 12 | Battery Pack | 18650 Li-ion, 3S2P (3 × 2 cells, ~11.1V nominal) | 1 | 800 | Simulated EV battery for demo |
| 13 | Battery Holder | 3S 18650 holder with leads | 1 | 120 | Holds the cell pack |
| 14 | Pull-up Resistors | 4.7 kΩ, 1/4W (DS18B20 1-Wire pull-up) | 2 | 5 | 1-Wire bus signal integrity |
| 15 | Breadboard | 830-point solderless breadboard | 1 | 120 | Prototyping platform |
| 16 | Jumper Wires | Male-to-male + male-to-female, 20 cm | 40 | 100 | Connections |
| 17 | USB Power Adapter | 5V 3A USB-A adapter | 1 | 250 | Powers ESP32 and all 3.3V/5V modules |
| 18 | USB Cable | Micro-USB or USB-C (match ESP32 board) | 1 | 80 | ESP32 programming + power |
| 19 | Multimeter | Any basic DMM (Uni-T UT33 or equivalent) | 1 | — | Verification and debugging |

**Total estimated BOM cost: ₹ 2,815** (excluding multimeter)

---

## Pin Mapping

### ESP32 DevKit v1 — Full Pin Assignment

```
ESP32 Pin       │ Signal        │ Connected To          │ Protocol
────────────────┼───────────────┼───────────────────────┼──────────
GPIO 5  (D5)    │ SS / SDA      │ MFRC522 SDA           │ SPI CS
GPIO 18 (D18)   │ SCK           │ MFRC522 SCK           │ SPI CLK
GPIO 23 (D23)   │ MOSI          │ MFRC522 MOSI          │ SPI
GPIO 19 (D19)   │ MISO          │ MFRC522 MISO          │ SPI
GPIO 2  (D2)    │ RST           │ MFRC522 RST           │ GPIO OUT
GPIO 21 (D21)   │ SDA           │ INA219 SDA, LCD SDA   │ I2C
GPIO 22 (D22)   │ SCL           │ INA219 SCL, LCD SCL   │ I2C
GPIO 4  (D4)    │ 1-Wire Data   │ DS18B20 DATA (both)   │ 1-Wire
GPIO 26 (D26)   │ Relay Control │ Relay IN              │ GPIO OUT
GPIO 27 (D27)   │ Buzzer        │ Buzzer +              │ GPIO OUT
GPIO 32 (D32)   │ LED Green     │ Green LED (+ 330Ω)    │ GPIO OUT
GPIO 33 (D33)   │ LED Red       │ Red LED (+ 330Ω)      │ GPIO OUT
3.3V            │ VCC           │ MFRC522, INA219       │ Power
5V (VIN)        │ VCC           │ Relay, Buzzer, LCD    │ Power
GND             │ GND           │ All modules           │ Common GND
```

> **Note:** The I2C bus has two devices: INA219 at address `0x40` and LCD (PCF8574) at `0x27`. Both share GPIO 21/22. This is valid — I2C is a multi-device bus. Ensure the PCF8574 address jumpers on the LCD backpack match `0x27` (A0=A1=A2=0).

---

## Circuit Schematic Description

A full schematic PDF is in `hardware/schematics/schematic.pdf`. The key sub-circuits are:

### RFID Reader (MFRC522)

```
ESP32 3.3V ──── VCC (MFRC522)
ESP32 GND  ──── GND (MFRC522)
GPIO 5     ──── SDA
GPIO 18    ──── SCK
GPIO 23    ──── MOSI
GPIO 19    ──── MISO
GPIO 2     ──── RST
           (IRQ — leave unconnected for this project)
```

**Important:** MFRC522 operates at **3.3V logic**. Do not connect to 5V pins. The ESP32 is 3.3V native — no level shifting required.

---

### INA219 (Power Sensor)

```
ESP32 3.3V ──── VCC
ESP32 GND  ──── GND
GPIO 21    ──── SDA
GPIO 22    ──── SCL
Battery +  ──── VIN+ (IN+ on module)
Relay Out+ ──── VIN- (IN- on module)
```

The INA219 measures current by sensing the voltage drop across an internal 0.1Ω shunt resistor. Place the INA219 **in series** on the positive charging line between the relay output and the battery pack positive terminal.

---

### DS18B20 Temperature Sensors

```
DS18B20 (cell probe):
  Red  (VDD) ──── 3.3V
  Black (GND) ──── GND
  Yellow (DQ) ──┬─ GPIO 4
                └─ 4.7kΩ ──── 3.3V   ← pull-up required

DS18B20 (ambient):
  Red  (VDD) ──── 3.3V
  Black (GND) ──── GND
  Yellow (DQ) ──── GPIO 4  (same bus as cell probe)
```

Both DS18B20 sensors share the same 1-Wire bus (GPIO 4). Only one 4.7kΩ pull-up resistor is needed for the entire bus, not one per sensor.

---

### Relay Module (Charging Circuit Control)

```
Relay Module:
  VCC ──── ESP32 5V
  GND ──── ESP32 GND
  IN  ──── GPIO 26

  COM (relay common) ──── TP4056 charging output positive
  NO  (normally open) ──── Battery pack positive terminal
```

When GPIO 26 is HIGH, the relay closes, connecting the charger to the battery. The relay module has a built-in flyback diode and transistor driver — no external components needed.

---

### LCD 20×4 with I2C Backpack

```
LCD + PCF8574 backpack:
  VCC ──── 5V
  GND ──── GND
  SDA ──── GPIO 21
  SCL ──── GPIO 22
```

The LCD requires 5V for the display panel but the PCF8574 I2C interface is 3.3V/5V compatible. On most clone modules, the I2C lines are pulled up to 5V — this is within the ESP32's absolute maximum rating (5V tolerant on most GPIO pins, but check your specific ESP32 board datasheet before connecting).

---

## Power Budget

| Module | VCC | Typical Current | Peak Current |
|---|---|---|---|
| ESP32 (Wi-Fi active) | 3.3V | 80 mA | 240 mA |
| MFRC522 | 3.3V | 13 mA | 26 mA |
| INA219 | 3.3V | 1 mA | 1 mA |
| DS18B20 × 2 | 3.3V | 2 mA | 2 mA |
| LCD + backlight | 5V | 30 mA | 50 mA |
| Relay coil | 5V | 70 mA | 90 mA |
| Buzzer | 5V | 30 mA | 30 mA |
| LEDs × 2 | 3.3V | 10 mA | 10 mA |
| **Total** | | **≈ 236 mA** | **≈ 449 mA** |

A 5V 3A USB power adapter provides 3000 mA — well above the 449 mA peak. The margin covers inrush and USB cable voltage drop.

---

## Hardware Assembly Notes

1. Build and test each module independently before connecting everything.
2. Use the I2C scanner sketch (`examples/Wire/i2c_scanner`) to verify INA219 (`0x40`) and LCD (`0x27`) addresses before flashing the main firmware.
3. Before connecting the battery pack, verify relay polarity with a multimeter in continuity mode — ensure the relay is open (no connection between COM and NO) when the ESP32 is unpowered.
4. The 18650 cells must be pre-charged to at least 3.0V/cell before use. Deeply discharged Li-ion cells may not be recoverable by the TP4056.
5. Never short the battery pack terminals — always add a main fuse (500mA fast-blow) in series with the positive terminal during development.
