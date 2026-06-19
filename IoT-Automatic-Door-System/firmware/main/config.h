#ifndef CONFIG_H
#define CONFIG_H

// ─── WiFi Credentials ────────────────────────────────────────────────────────
#define WIFI_SSID         "YOUR_WIFI_SSID"
#define WIFI_PASSWORD     "YOUR_WIFI_PASSWORD"
#define WIFI_TIMEOUT_MS   10000

// ─── MQTT Broker ─────────────────────────────────────────────────────────────
#define MQTT_SERVER       "192.168.1.100"   // Replace with broker IP or hostname
#define MQTT_PORT         1883
#define MQTT_CLIENT_ID    "esp32_door_01"
#define MQTT_USER         ""                // Leave empty if no auth
#define MQTT_PASS         ""

// ─── MQTT Topics ─────────────────────────────────────────────────────────────
#define TOPIC_STATUS      "door/status"     // Publish: OPEN / CLOSED / ERROR
#define TOPIC_EVENT       "door/event"      // Publish: JSON access event
#define TOPIC_COMMAND     "door/command"    // Subscribe: OPEN / CLOSE / STATUS
#define TOPIC_HEARTBEAT   "door/heartbeat"  // Publish: uptime + sensor state

// ─── GPIO Pin Assignments ────────────────────────────────────────────────────
#define PIN_PIR           13
#define PIN_TRIG          14
#define PIN_ECHO          27
#define PIN_RFID_CS        5
#define PIN_RFID_RST      22
#define PIN_SERVO         25
#define PIN_RELAY         26
#define PIN_BUZZER        32
#define PIN_LED_RED       33
#define PIN_LED_GREEN     34
#define PIN_BUTTON_IN      4
#define PIN_BUTTON_OUT    35

// ─── Door Timing ─────────────────────────────────────────────────────────────
#define DOOR_OPEN_ANGLE       90          // Servo degrees for open position
#define DOOR_CLOSE_ANGLE       0          // Servo degrees for closed position
#define AUTO_CLOSE_MS       5000          // ms before door auto-closes
#define SERVO_MOVE_DELAY_MS   15          // ms between servo degree steps

// ─── Sensor Thresholds ───────────────────────────────────────────────────────
#define PIR_WARMUP_MS        2000         // PIR calibration time at boot
#define ULTRASONIC_TRIGGER_CM  100        // Motion zone boundary (cm)
#define ULTRASONIC_OBSTACLE_CM  10        // Door-crush prevention threshold
#define ULTRASONIC_TIMEOUT_US 30000       // Echo timeout (microseconds)

// ─── System ──────────────────────────────────────────────────────────────────
#define HEARTBEAT_INTERVAL_MS 30000       // How often to publish heartbeat
#define SERIAL_BAUD           115200
#define OTA_HOSTNAME          "esp32-door"
#define OTA_PASSWORD          "ota_password"

// ─── Authorized RFID UIDs ────────────────────────────────────────────────────
// Add card UIDs as hex strings (read from Serial monitor on first scan)
const char* AUTHORIZED_UIDS[] = {
    "A1B2C3D4",
    "11223344",
    "DEADBEEF",
};
const int AUTHORIZED_COUNT = sizeof(AUTHORIZED_UIDS) / sizeof(AUTHORIZED_UIDS[0]);

#endif // CONFIG_H
