#ifndef CONFIG_H
#define CONFIG_H

// ─── Wi-Fi ────────────────────────────────────────────────────────────────────
#define WIFI_SSID         "YourWiFiSSID"
#define WIFI_PASSWORD     "YourWiFiPassword"

// ─── MQTT ─────────────────────────────────────────────────────────────────────
#define MQTT_BROKER       "192.168.1.100"
#define MQTT_PORT         1883
#define MQTT_CLIENT_ID    "ev_charger_01"

// MQTT Topics
#define TOPIC_TELEMETRY   "ev/telemetry"
#define TOPIC_SESSION     "ev/session"
#define TOPIC_FAULT       "ev/fault"
#define MQTT_PUBLISH_INTERVAL_MS  5000UL

// ─── Pin Definitions ──────────────────────────────────────────────────────────
#define PIN_RFID_SS       5
#define PIN_RFID_RST      2
#define PIN_DS18B20       4
#define PIN_RELAY         26
#define PIN_BUZZER        27
#define PIN_LED_GREEN     32
#define PIN_LED_RED       33

// ─── I2C (INA219 + LCD share the bus) ────────────────────────────────────────
#define I2C_SDA           21
#define I2C_SCL           22
#define INA219_ADDR       0x40
#define LCD_ADDR          0x27
#define LCD_COLS          20
#define LCD_ROWS          4

// ─── Battery / Safety Thresholds ──────────────────────────────────────────────
#define CELL_COUNT        3            // 3S Li-ion pack
#define VOLT_CUTOFF_PER_CELL  4.25f   // Volts — overvoltage protection
#define VOLT_MIN_PER_CELL     3.0f    // Volts — undervoltage protection
#define CURRENT_MAX_A         4.5f    // Amps — overcurrent protection
#define TEMP_CUTOFF_C         45.0f   // °C — thermal protection
#define TEMP_WARN_C           40.0f   // °C — warning threshold

// ─── SOC Estimation ───────────────────────────────────────────────────────────
#define BATTERY_CAPACITY_MAH  4000    // mAh (2P × 2000mAh cells)
#define SOC_FULL_VOLTAGE      4.20f   // V/cell — 100% SOC
#define SOC_EMPTY_VOLTAGE     3.00f   // V/cell — 0% SOC

// ─── Payment ──────────────────────────────────────────────────────────────────
#define UNIT_RATE_RS      8.0f        // ₹ per kWh (configurable)

// ─── EEPROM Layout ────────────────────────────────────────────────────────────
#define EEPROM_SIZE           512
#define EEPROM_ADDR_UID_BASE  0       // First 20 bytes: 4 stored UIDs (5B each)
#define EEPROM_ADDR_LOG_BASE  20      // Session logs start at byte 20
#define MAX_SESSION_LOGS      20
#define SESSION_LOG_SIZE      24      // Bytes per log entry

// ─── Timing ───────────────────────────────────────────────────────────────────
#define SENSOR_POLL_INTERVAL_MS   1000UL
#define LCD_UPDATE_INTERVAL_MS    1000UL
#define BUZZER_BEEP_SHORT_MS      100UL
#define BUZZER_BEEP_LONG_MS       500UL
#define LCD_BILL_DISPLAY_MS       10000UL

#endif // CONFIG_H
