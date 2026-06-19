# Hardware Components

## Bill of Materials (BOM)

| # | Component | Model | Qty | Unit Cost (₹) | Total (₹) | Datasheet |
|---|-----------|-------|-----|---------------|-----------|-----------|
| 1 | Microcontroller | ESP32 Dev Module (38-pin) | 1 | 400 | 400 | [Espressif](https://www.espressif.com/sites/default/files/documentation/esp32_datasheet_en.pdf) |
| 2 | PIR Motion Sensor | HC-SR501 | 1 | 80 | 80 | [Datasheet](https://www.mpja.com/download/31227sc.pdf) |
| 3 | Ultrasonic Sensor | HC-SR04 | 1 | 60 | 60 | [Datasheet](https://cdn.sparkfun.com/datasheets/Sensors/Proximity/HCSR04.pdf) |
| 4 | RFID Module + Cards | RC522 (13.56 MHz SPI) | 1 | 120 | 120 | [Datasheet](https://www.nxp.com/docs/en/data-sheet/MFRC522.pdf) |
| 5 | Servo Motor | MG996R Metal Gear | 1 | 250 | 250 | [Datasheet](https://www.electronicoscaldas.com/datasheet/MG996R_Tower-Pro.pdf) |
| 6 | DC Motor Driver | L298N H-Bridge Module | 1 | 80 | 80 | [Datasheet](https://www.st.com/resource/en/datasheet/l298.pdf) |
| 7 | Relay Module | SRD-05VDC-SL-C 5V | 1 | 60 | 60 | — |
| 8 | LCD Display | I2C 16×2 (PCF8574 backpack) | 1 | 120 | 120 | — |
| 9 | Buzzer | Active Piezo 5V | 1 | 30 | 30 | — |
| 10 | RGB LED | Common Cathode 5mm | 3 | 5 | 15 | — |
| 11 | Push Button | Momentary SPST 6×6mm | 2 | 5 | 10 | — |
| 12 | Resistors | 220Ω, 10kΩ | 10 | 1 | 10 | — |
| 13 | Power Supply | 5V 3A USB-C adapter | 1 | 150 | 150 | — |
| 14 | LiPo Battery | 3.7V 2000mAh + TP4056 charger | 1 | 200 | 200 | — |
| 15 | Jumper Wires | M-M / M-F 20cm | 40 | 2 | 80 | — |
| 16 | Breadboard | 830-tie point | 1 | 80 | 80 | — |
| 17 | PCB / Stripboard | 7×9 cm | 1 | 30 | 30 | — |

**Total estimated cost: ₹1,775 (≈ USD 21)**

---

## Wiring Reference

### ESP32 → HC-SR501 (PIR)
```
VCC  → 3.3V (or 5V via step-up)
GND  → GND
OUT  → GPIO 13
```
> Adjust sensitivity and delay trimpots: sensitivity fully CCW = 3 m range, delay CCW = 3 s hold

### ESP32 → HC-SR04 (Ultrasonic)
```
VCC  → 5V
GND  → GND
TRIG → GPIO 14
ECHO → GPIO 27  (use 1kΩ + 2kΩ voltage divider — HC-SR04 outputs 5V, ESP32 is 3.3V tolerant only)
```

### ESP32 → RC522 (RFID via SPI)
```
3.3V → 3.3V      (NEVER connect to 5V — damages RC522)
GND  → GND
SDA  → GPIO 5    (SPI CS)
SCK  → GPIO 18
MOSI → GPIO 23
MISO → GPIO 19
RST  → GPIO 22
IRQ  → NC        (not used)
```

### ESP32 → MG996R (Servo)
```
Red    → 5V (external supply recommended for high torque)
Brown  → GND (common with ESP32 GND)
Orange → GPIO 25 (PWM signal)
```

### ESP32 → Relay Module
```
VCC → 5V
GND → GND
IN  → GPIO 26
```

### ESP32 → I2C LCD (PCF8574)
```
VCC → 5V
GND → GND
SDA → GPIO 21
SCL → GPIO 22
```
> Default I2C address: 0x27. Run I2C scanner if LCD does not respond.

### ESP32 → Buzzer
```
+   → GPIO 32 (via 100Ω resistor)
-   → GND
```

### ESP32 → LEDs
```
Red LED   Anode → GPIO 33 (via 220Ω)  Cathode → GND
Green LED Anode → GPIO 34 (via 220Ω)  Cathode → GND
```

---

## Power Budget

| Component | Typical Current | Peak Current |
|-----------|----------------|-------------|
| ESP32 (WiFi active) | 160 mA | 240 mA |
| ESP32 (light sleep) | 0.8 mA | — |
| HC-SR501 | 65 µA | — |
| HC-SR04 | 15 mA | — |
| RC522 | 13 mA | 26 mA |
| MG996R Servo (moving) | 500 mA | 2.5 A |
| MG996R Servo (hold) | 150 mA | — |
| Relay coil | 70 mA | — |
| LCD (backlight on) | 30 mA | — |
| **Total (active)** | **~960 mA** | **~3 A** |

**Recommendation:** 5V 3A power supply; use 5V 5A if using heavy-duty DC door motor.

---

## Tools Required

- Soldering iron + solder
- Multimeter
- Wire stripper
- Phillips screwdriver
- Hot glue gun (for cable management)
- USB-A to USB-C cable (for ESP32 flashing)
