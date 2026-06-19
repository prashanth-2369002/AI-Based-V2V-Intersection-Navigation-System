# Future Improvements

This document outlines realistic next steps that follow logically from the current prototype. Each item is technically grounded — no item requires fabricated hardware or impossible results.

---

## High Priority

### 1. OCPP 1.6 Protocol Implementation

**What it is:** Open Charge Point Protocol (OCPP) is the industry standard for communication between EV charge points and a central management system (CSMS). It runs over WebSocket.

**Why it matters:** Without OCPP, the station cannot be registered with commercial charging networks (Tata Power EZ Charge, Ather Grid, etc.) or fleet management platforms.

**What needs to change:**
- Replace the custom MQTT telemetry with OCPP 1.6 JSON messages (`BootNotification`, `Heartbeat`, `StartTransaction`, `StopTransaction`, `MeterValues`).
- Requires switching the ESP32 MQTT client for a WebSocket client library (e.g., `arduinoWebSockets`).
- A free open-source CSMS like [SteVe](https://github.com/steve-community/steve) can be used as the backend.

**Estimated effort:** 3–4 weeks for a working OCPP 1.6 Core Profile implementation.

---

### 2. GSM / 4G Fallback Connectivity

**What it is:** Add a SIM800L or SIM7600 GSM module as a secondary network interface when Wi-Fi is unavailable.

**Why it matters:** Outdoor charging stations rarely have reliable Wi-Fi coverage. GSM ensures data continuity.

**What needs to change:**
- Add a SIM800L module on UART2 (GPIO 16/17).
- Implement a connection manager that switches between Wi-Fi and GSM based on `WiFi.status()`.
- MQTT over GPRS is achievable at low data rates (telemetry JSON is ~150 bytes per message).

**Known constraint:** SIM800L supports only 2G. In areas where 2G is being phased out (urban India), the SIM7600 (4G LTE) module is preferred.

---

## Medium Priority

### 3. Mobile App (Flutter)

**What it is:** A cross-platform mobile app (Android + iOS) to replace the browser dashboard.

**Features to add:**
- Push notifications on session start/end (via Firebase Cloud Messaging).
- Session history with filter by date.
- QR code display for payment.
- Native SOC gauge widget.

**What needs to change on the backend:** Add JWT-based authentication to Flask routes. Expose a `/api/auth` endpoint for login. Use Flask-JWT-Extended.

---

### 4. UPI / QR Code Payment Integration

**What it is:** Replace the post-pay ledger model with a pre-pay or instant-pay flow using UPI deep links or Razorpay API.

**Flow:**
1. User scans QR code displayed on LCD or mobile app.
2. UPI payment is made via any UPI app.
3. Razorpay webhook confirms payment to the Flask backend.
4. Flask backend publishes an MQTT `unlock` command.
5. ESP32 opens the relay only after payment confirmation.

**Constraint:** Razorpay API requires a registered business account. Test mode is free. Full production requires RBI compliance for payment collection.

---

### 5. Multi-Port Charging Station

**What it is:** Expand from 1 charging port to 4 ports managed by a single ESP32 (or ESP32-S3 for more GPIO).

**Architecture change:**
- 4 relay modules on separate GPIO pins.
- 4 INA219 sensors on the same I2C bus (different I2C addresses: 0x40, 0x41, 0x44, 0x45 — selectable via A0/A1 pins).
- Shared BMS logic, separate session state per port.
- MQTT topic becomes `ev/port/1/telemetry`, `ev/port/2/telemetry`, etc.

**Known constraint:** DS18B20 sensors share one 1-Wire bus; up to 8 sensors can coexist on a single pin. Each sensor has a factory-programmed 64-bit ROM code used for addressing.

---

## Low Priority

### 6. Solar PV Input Integration

**What it is:** Add a solar panel with an MPPT charge controller (e.g., CN3791 or a commercial unit like EPSolar VS-series) to provide solar-assisted charging.

**What changes in firmware:**
- Monitor a second INA219 on the solar input line.
- Track solar energy contribution separately (`solar_wh` vs `grid_wh`).
- Publish both values in telemetry so the dashboard can show the renewable fraction.

**Constraint:** An MPPT controller handles the panel-to-battery conversion. The ESP32 only monitors; it does not control the MPPT.

---

### 7. Cloud Deployment (AWS IoT Core)

**What it is:** Replace local Mosquitto with AWS IoT Core as the MQTT broker, and deploy the Flask dashboard on an EC2 instance or as a Lambda + API Gateway serverless app.

**What changes:**
- AWS IoT Core requires TLS and X.509 certificate authentication. The ESP32 must store the device certificate and private key (in SPIFFS).
- PubSubClient supports TLS via `WiFiClientSecure`.
- The Flask app connects to IoT Core using the `AWSIoTPythonSDK` or `boto3`.

**Cost estimate:** AWS IoT Core free tier covers 500,000 messages/month. At 1 message/5s, a single station sends ~518,400 messages/month — just at the free tier limit.

---

## Not in Scope

The following items are intentionally excluded from this project's roadmap because they require regulatory certification, utility grid approvals, or specialised hardware beyond a diploma project:

- **AC grid connection:** Any connection to the domestic/commercial grid requires approval from the State Electricity Board and compliance with IE Rules 2023.
- **Type 2 / CCS2 / CHAdeMO connector:** These connectors require IEC 62196 certified hardware and interoperability testing.
- **DC fast charging (>3.3kW):** Requires power electronics design far beyond the scope of an embedded systems diploma project.
- **Vehicle-to-Grid (V2G):** Requires bidirectional inverter hardware and grid synchronisation, which is a standalone research field.
