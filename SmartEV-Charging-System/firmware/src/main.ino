/*
 * Smart EV Charging System — Main Firmware
 * Platform : ESP32 DevKit v1
 * Author   : [Your Name]
 * Version  : 1.0.0
 *
 * State machine:
 *   IDLE → AUTHENTICATING → CHARGING → (BALANCING) → FULL
 *                       ↘ FAULT (any protection trip)
 */

#include <Arduino.h>
#include <SPI.h>
#include <MFRC522.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

#include "config.h"
#include "bms.h"
#include "auth.h"
#include "payment.h"

// ─── Peripheral objects ───────────────────────────────────────────────────────
MFRC522           rfid(PIN_RFID_SS, PIN_RFID_RST);
LiquidCrystal_I2C lcd(LCD_ADDR, LCD_COLS, LCD_ROWS);
WiFiClient        wifiClient;
PubSubClient      mqttClient(wifiClient);
BMS               bms;
Auth              auth(rfid);
Payment           payment;

// ─── System state ─────────────────────────────────────────────────────────────
enum class State { IDLE, CHARGING, FAULT, FULL };
State state = State::IDLE;

// ─── Timers ───────────────────────────────────────────────────────────────────
unsigned long lastSensorPoll  = 0;
unsigned long lastMqttPublish = 0;
unsigned long lastLcdUpdate   = 0;

// ─── Forward declarations ─────────────────────────────────────────────────────
void connectWiFi();
void connectMQTT();
void publishTelemetry(const BatteryData& data);
void publishSessionEvent(const char* event, const SessionRecord* rec = nullptr);
void updateLCD(const BatteryData& data);
void showBillOnLCD(const SessionRecord& rec);
void beep(int count, int durationMs);
void setRelay(bool on);

// ─────────────────────────────────────────────────────────────────────────────

void setup() {
    Serial.begin(115200);

    pinMode(PIN_RELAY,     OUTPUT);
    pinMode(PIN_BUZZER,    OUTPUT);
    pinMode(PIN_LED_GREEN, OUTPUT);
    pinMode(PIN_LED_RED,   OUTPUT);
    setRelay(false);

    Wire.begin(I2C_SDA, I2C_SCL);
    SPI.begin();

    lcd.init();
    lcd.backlight();
    lcd.setCursor(0, 0);
    lcd.print("Smart EV Charger");
    lcd.setCursor(0, 1);
    lcd.print("Initialising...");

    bms.begin();
    auth.begin();
    rfid.PCD_Init();

    connectWiFi();
    mqttClient.setServer(MQTT_BROKER, MQTT_PORT);

    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("System Ready");
    lcd.setCursor(0, 1);
    lcd.print("Tap card to start");

    beep(2, BUZZER_BEEP_SHORT_MS);
}

void loop() {
    if (!mqttClient.connected()) connectMQTT();
    mqttClient.loop();

    unsigned long now = millis();

    // ── Sensor polling ────────────────────────────────────────────────────────
    if (now - lastSensorPoll >= SENSOR_POLL_INTERVAL_MS) {
        lastSensorPoll = now;

        if (state == State::CHARGING) {
            BatteryData data = bms.read();

            if (data.isFault) {
                state = State::FAULT;
                setRelay(false);
                beep(3, BUZZER_BEEP_LONG_MS);
                digitalWrite(PIN_LED_RED, HIGH);
                lcd.clear();
                lcd.setCursor(0, 0);
                lcd.print("! FAULT !");
                lcd.setCursor(0, 1);
                lcd.print(data.faultReason);
                publishSessionEvent("fault");
                return;
            }

            if (data.soc >= 100.0f) {
                state = State::FULL;
                setRelay(false);
                beep(3, BUZZER_BEEP_SHORT_MS);
                SessionRecord rec = payment.endSession(bms.getSessionEnergy());
                payment.logToEEPROM(rec);
                publishSessionEvent("session_end", &rec);
                showBillOnLCD(rec);
                state = State::IDLE;
                return;
            }

            // LCD update (throttled separately)
            if (now - lastLcdUpdate >= LCD_UPDATE_INTERVAL_MS) {
                lastLcdUpdate = now;
                updateLCD(data);
            }

            // MQTT publish
            if (now - lastMqttPublish >= MQTT_PUBLISH_INTERVAL_MS) {
                lastMqttPublish = now;
                publishTelemetry(data);
            }
        }
    }

    // ── RFID card poll ────────────────────────────────────────────────────────
    if (state == State::IDLE || state == State::CHARGING) {
        bool valid = auth.poll();

        if (valid) {
            if (state == State::IDLE) {
                // Start session
                bms.resetSession();
                payment.startSession(auth.getLastUID());
                setRelay(true);
                state = State::CHARGING;
                beep(1, BUZZER_BEEP_SHORT_MS);
                digitalWrite(PIN_LED_GREEN, HIGH);
                publishSessionEvent("session_start");
                lcd.clear();
                lcd.setCursor(0, 0);
                lcd.print("Charging Started");

            } else if (state == State::CHARGING) {
                // End session
                setRelay(false);
                float energy = bms.getSessionEnergy();
                SessionRecord rec = payment.endSession(energy);
                payment.logToEEPROM(rec);
                publishSessionEvent("session_end", &rec);
                beep(2, BUZZER_BEEP_SHORT_MS);
                digitalWrite(PIN_LED_GREEN, LOW);
                showBillOnLCD(rec);
                state = State::IDLE;
            }

        } else if (rfid.uid.size > 0) {
            // Card presented but not authorised
            lcd.clear();
            lcd.setCursor(0, 0);
            lcd.print("Access Denied");
            lcd.setCursor(0, 1);
            lcd.print(auth.getLastUID());
            beep(1, BUZZER_BEEP_LONG_MS);
            delay(2000);
            lcd.clear();
            lcd.setCursor(0, 0);
            lcd.print("Tap card to start");
        }
    }

    if (state == State::FAULT) {
        // Wait for manual clear (tap any registered card)
        if (auth.poll()) {
            bms.clearFault();
            state = State::IDLE;
            digitalWrite(PIN_LED_RED, LOW);
            lcd.clear();
            lcd.setCursor(0, 0);
            lcd.print("Fault Cleared");
            lcd.setCursor(0, 1);
            lcd.print("Tap card to start");
            beep(1, BUZZER_BEEP_SHORT_MS);
        }
    }
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

void connectWiFi() {
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    lcd.setCursor(0, 2);
    lcd.print("WiFi connecting");
    int tries = 0;
    while (WiFi.status() != WL_CONNECTED && tries < 20) {
        delay(500);
        tries++;
    }
    if (WiFi.status() == WL_CONNECTED) {
        lcd.setCursor(0, 2);
        lcd.print("WiFi OK          ");
    } else {
        lcd.setCursor(0, 2);
        lcd.print("WiFi FAIL-offline");
    }
}

void connectMQTT() {
    int tries = 0;
    while (!mqttClient.connected() && tries < 3) {
        mqttClient.connect(MQTT_CLIENT_ID);
        tries++;
        delay(500);
    }
}

void publishTelemetry(const BatteryData& data) {
    StaticJsonDocument<256> doc;
    doc["uid"]       = auth.getLastUID();
    doc["voltage"]   = serialized(String(data.voltage, 2));
    doc["current"]   = serialized(String(data.current, 3));
    doc["power_w"]   = serialized(String(data.powerW, 2));
    doc["energy_wh"] = serialized(String(data.energyWh, 3));
    doc["soc"]       = serialized(String(data.soc, 1));
    doc["temp_c"]    = serialized(String(data.temperature, 1));
    doc["elapsed_s"] = payment.getElapsedSeconds();

    char buf[256];
    serializeJson(doc, buf, sizeof(buf));
    mqttClient.publish(TOPIC_TELEMETRY, buf);
}

void publishSessionEvent(const char* event, const SessionRecord* rec) {
    StaticJsonDocument<256> doc;
    doc["event"] = event;
    doc["uid"]   = auth.getLastUID();
    if (rec) {
        doc["energy_wh"] = serialized(String(rec->energyWh, 2));
        doc["cost_rs"]   = serialized(String(rec->costRs, 2));
        doc["duration_s"] = (rec->endMs - rec->startMs) / 1000UL;
    }
    char buf[256];
    serializeJson(doc, buf, sizeof(buf));
    mqttClient.publish(TOPIC_SESSION, buf);
}

void updateLCD(const BatteryData& data) {
    lcd.setCursor(0, 0);
    lcd.printf("SOC: %5.1f%%  %4.1fV", data.soc, data.voltage);
    lcd.setCursor(0, 1);
    lcd.printf("I: %4.2fA  P: %5.1fW", data.current, data.powerW);
    lcd.setCursor(0, 2);
    lcd.printf("Temp: %4.1fC         ", data.temperature);
    unsigned long elapsed = payment.getElapsedSeconds();
    lcd.setCursor(0, 3);
    lcd.printf("Time: %02lu:%02lu:%02lu", elapsed / 3600, (elapsed % 3600) / 60, elapsed % 60);
}

void showBillOnLCD(const SessionRecord& rec) {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Session Complete");
    lcd.setCursor(0, 1);
    lcd.printf("Energy: %.2f Wh", rec.energyWh);
    lcd.setCursor(0, 2);
    lcd.printf("Cost:   Rs %.2f", rec.costRs);
    lcd.setCursor(0, 3);
    unsigned long dur = (rec.endMs - rec.startMs) / 1000UL;
    lcd.printf("Time: %02lu:%02lu:%02lu", dur / 3600, (dur % 3600) / 60, dur % 60);
    delay(LCD_BILL_DISPLAY_MS);
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Tap card to start");
}

void beep(int count, int durationMs) {
    for (int i = 0; i < count; i++) {
        digitalWrite(PIN_BUZZER, HIGH);
        delay(durationMs);
        digitalWrite(PIN_BUZZER, LOW);
        if (i < count - 1) delay(100);
    }
}

void setRelay(bool on) {
    digitalWrite(PIN_RELAY, on ? HIGH : LOW);
}
