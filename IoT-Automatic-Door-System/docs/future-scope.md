# Future Scope

## Roadmap

### Phase 2 — Enhanced Authentication (Near-term)

| Feature | Technology | Effort | Impact |
|---------|-----------|--------|--------|
| **Face recognition unlock** | ESP32-CAM + TensorFlow Lite MobileNet | High | High |
| **Fingerprint biometric** | R307 / AS608 optical sensor | Medium | High |
| **NFC smartphone tap** | PN532 + NDEF | Medium | High |
| **PIN keypad fallback** | 4×4 matrix keypad | Low | Medium |
| **Bluetooth proximity** | ESP32 BLE beacon + phone RSSI | Medium | Medium |

**Face recognition concept:**
```
ESP32-CAM captures frame (JPEG 320×240)
  → Run on-device MobileNetV2 (quantized INT8, ~400ms inference)
  → Match against enrolled face embeddings (stored in SPIFFS)
  → Grant/deny + log event
```

---

### Phase 3 — Cloud Integration (Medium-term)

| Feature | Technology | Benefit |
|---------|-----------|---------|
| **AWS IoT Core** | MQTT over TLS to AWS | Scalable multi-door |
| **Firebase Realtime DB** | ESP32 → Firebase REST | No broker needed |
| **Push notifications** | Firebase Cloud Messaging | Instant access alerts on phone |
| **Cloud access log analytics** | AWS QuickSight / Grafana | Trend visualization |
| **Remote UID management** | REST API → MQTT → ESP32 NVS | Add/revoke cards without reflash |

---

### Phase 4 — AI & Anomaly Detection (Long-term)

| Feature | Description |
|---------|-------------|
| **Tailgating detection** | Count people via ESP32-CAM — alert if 2+ enter on 1 scan |
| **Unusual-hours alert** | ML model trained on access patterns — alert on out-of-hours entry |
| **Liveness detection** | Prevent RFID photo spoofing with IR blink test |
| **Edge anomaly model** | TFLite model on ESP32 detects abnormal motion patterns |
| **Predictive maintenance** | Servo current monitoring predicts wear before failure |

---

### Phase 5 — Deployment-grade (Future)

| Improvement | Detail |
|-------------|--------|
| **Multi-door network** | MQTT topic hierarchy: `site/building/floor/door/command` |
| **Solar + battery** | 6W panel + 18650 pack for off-grid operation |
| **PCB design** | Custom KiCad PCB replaces breadboard — vibration-resistant |
| **3D-printed enclosure** | PETG enclosure with IP44 rating (dust/water-resistant) |
| **PoE option** | Power over Ethernet eliminates separate power run |
| **Encrypted RFID** | Migrate from Mifare Classic (broken) to DESFire EV2 AES-128 |
| **Visitor management** | Pre-authorize temp cards with expiry, log to company directory |
| **Voice assistant** | "Hey Google, open front door" via Home Assistant integration |

---

## Integration Opportunities

### Home Assistant
```yaml
# configuration.yaml
mqtt:
  switch:
    - name: "Front Door"
      command_topic: "door/command"
      state_topic:   "door/status"
      payload_on:    "OPEN"
      payload_off:   "CLOSE"
      state_value_template: "{{ value_json.state }}"
```

### Node-RED Dashboard
Import the flow from `scripts/nodered_flow.json` to get:
- Real-time door status gauge
- Access event table (auto-refreshes)
- Remote open/close toggle button
- 24-hour access timeline chart

### IFTTT / Zapier
Trigger webhooks from MQTT events via Node-RED HTTP node:
- "Send Slack message when access denied 3+ times in 1 minute"
- "Log visitor entries to Google Sheets"
- "Turn on porch light when door opens after sunset"
