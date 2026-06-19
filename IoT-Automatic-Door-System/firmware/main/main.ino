/*
 * IoT-Based Automatic Door System
 * Main firmware — ESP32
 *
 * Sensor stack : PIR (HC-SR501) + Ultrasonic (HC-SR04) + RFID (RC522)
 * Actuator     : Servo motor (MG996R) + Relay
 * Comms        : WiFi + MQTT (PubSubClient)
 * UI           : I2C LCD 16x2 + RGB LEDs + Buzzer
 *
 * Author  : M Prashanth
 * License : MIT
 */

#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ESP32Servo.h>
#include <MFRC522.h>
#include <LiquidCrystal_I2C.h>
#include <ArduinoJson.h>
#include <ArduinoOTA.h>
#include <SPI.h>
#include "config.h"

// ─── Object Instances ─────────────────────────────────────────────────────────
WiFiClient        wifiClient;
PubSubClient      mqtt(wifiClient);
Servo             doorServo;
MFRC522           rfid(PIN_RFID_CS, PIN_RFID_RST);
LiquidCrystal_I2C lcd(0x27, 16, 2);

// ─── State Machine ────────────────────────────────────────────────────────────
enum DoorState { DOOR_CLOSED, DOOR_OPENING, DOOR_OPEN, DOOR_CLOSING, DOOR_ERROR };
DoorState doorState = DOOR_CLOSED;

// ─── Timing ───────────────────────────────────────────────────────────────────
unsigned long doorOpenedAt    = 0;
unsigned long lastHeartbeat   = 0;
unsigned long lastMqttRetry   = 0;

// ─── Forward declarations ─────────────────────────────────────────────────────
void connectWiFi();
void connectMQTT();
void mqttCallback(char* topic, byte* payload, unsigned int length);
void openDoor(const char* reason);
void closeDoor();
long readUltrasonic();
bool checkRFID(String& uid);
bool isAuthorized(const String& uid);
void publishEvent(const char* event, const char* uid, const char* reason);
void publishStatus();
void showLCD(const char* line1, const char* line2);
void buzzerAlert(int times, int durationMs);
void setLED(bool red, bool green);

// ─── Setup ────────────────────────────────────────────────────────────────────
void setup() {
    Serial.begin(SERIAL_BAUD);
    Serial.println(F("\n[BOOT] IoT Automatic Door System v1.0"));

    // GPIO init
    pinMode(PIN_PIR,        INPUT);
    pinMode(PIN_BUZZER,     OUTPUT);
    pinMode(PIN_LED_RED,    OUTPUT);
    pinMode(PIN_LED_GREEN,  OUTPUT);
    pinMode(PIN_RELAY,      OUTPUT);
    pinMode(PIN_BUTTON_IN,  INPUT_PULLUP);
    pinMode(PIN_BUTTON_OUT, INPUT_PULLUP);
    digitalWrite(PIN_RELAY, LOW);   // ensure door locked at boot

    // LCD
    lcd.init();
    lcd.backlight();
    showLCD("  Smart Door  ", "  Starting...  ");

    // Servo
    doorServo.attach(PIN_SERVO);
    doorServo.write(DOOR_CLOSE_ANGLE);

    // RFID
    SPI.begin();
    rfid.PCD_Init();
    Serial.println(F("[RFID] Reader initialized"));

    // PIR warmup
    Serial.print(F("[PIR] Warming up"));
    for (int i = 0; i < (PIR_WARMUP_MS / 200); i++) {
        delay(200);
        Serial.print('.');
    }
    Serial.println(F(" ready"));

    // Network
    connectWiFi();
    mqtt.setServer(MQTT_SERVER, MQTT_PORT);
    mqtt.setCallback(mqttCallback);
    connectMQTT();

    // OTA
    ArduinoOTA.setHostname(OTA_HOSTNAME);
    ArduinoOTA.setPassword(OTA_PASSWORD);
    ArduinoOTA.onStart([]() { showLCD("OTA Update", "In progress..."); });
    ArduinoOTA.onEnd([]()   { showLCD("OTA Done", "Rebooting..."); });
    ArduinoOTA.begin();

    showLCD("  Door Ready  ", " Scan card...  ");
    setLED(false, true);
    Serial.println(F("[BOOT] System ready"));
}

// ─── Main Loop ────────────────────────────────────────────────────────────────
void loop() {
    ArduinoOTA.handle();

    // Reconnect if dropped
    if (!mqtt.connected()) {
        if (millis() - lastMqttRetry > 5000) {
            lastMqttRetry = millis();
            connectMQTT();
        }
    }
    mqtt.loop();

    // Heartbeat
    if (millis() - lastHeartbeat > HEARTBEAT_INTERVAL_MS) {
        lastHeartbeat = millis();
        publishStatus();
    }

    // Manual override buttons
    if (digitalRead(PIN_BUTTON_IN) == LOW || digitalRead(PIN_BUTTON_OUT) == LOW) {
        delay(50); // debounce
        if (doorState == DOOR_CLOSED) openDoor("button");
        else if (doorState == DOOR_OPEN) closeDoor();
        while (digitalRead(PIN_BUTTON_IN) == LOW || digitalRead(PIN_BUTTON_OUT) == LOW);
    }

    // Auto-close timer
    if (doorState == DOOR_OPEN && millis() - doorOpenedAt > AUTO_CLOSE_MS) {
        long dist = readUltrasonic();
        if (dist < 0 || dist > ULTRASONIC_OBSTACLE_CM) {
            closeDoor();
        } else {
            Serial.println(F("[SAFETY] Obstacle detected — holding door open"));
            doorOpenedAt = millis();   // reset timer
        }
    }

    // Only run detection logic when door is closed
    if (doorState != DOOR_CLOSED) return;

    bool pirTriggered = digitalRead(PIN_PIR) == HIGH;
    if (!pirTriggered) return;

    long distCm = readUltrasonic();
    Serial.printf("[SENSOR] PIR=1  Distance=%ld cm\n", distCm);
    if (distCm < 0 || distCm > ULTRASONIC_TRIGGER_CM) return;

    // Try RFID (non-blocking — only if card is present)
    String uid;
    if (checkRFID(uid)) {
        if (isAuthorized(uid)) {
            Serial.printf("[AUTH] RFID granted: %s\n", uid.c_str());
            openDoor("rfid");
            publishEvent("ACCESS_GRANTED", uid.c_str(), "rfid");
        } else {
            Serial.printf("[AUTH] RFID denied: %s\n", uid.c_str());
            showLCD("Access Denied", uid.c_str());
            setLED(true, false);
            buzzerAlert(3, 200);
            delay(1500);
            showLCD("  Door Ready  ", " Scan card...  ");
            setLED(false, true);
            publishEvent("ACCESS_DENIED", uid.c_str(), "unauthorized_rfid");
        }
    } else if (distCm <= 30) {
        // Proximity-only unlock (guest / no-RFID mode)
        openDoor("proximity");
        publishEvent("ACCESS_GRANTED", "NONE", "proximity");
    }

    delay(200);
}

// ─── Door Control ─────────────────────────────────────────────────────────────
void openDoor(const char* reason) {
    if (doorState == DOOR_OPEN || doorState == DOOR_OPENING) return;
    doorState = DOOR_OPENING;
    showLCD("  Opening...  ", "");
    setLED(false, true);
    buzzerAlert(1, 100);
    digitalWrite(PIN_RELAY, HIGH);

    for (int angle = DOOR_CLOSE_ANGLE; angle <= DOOR_OPEN_ANGLE; angle++) {
        doorServo.write(angle);
        delay(SERVO_MOVE_DELAY_MS);
    }

    doorState = DOOR_OPEN;
    doorOpenedAt = millis();
    showLCD("   Door Open  ", "Auto-close: 5s ");
    publishEvent("DOOR_OPENED", "SYSTEM", reason);
    Serial.printf("[DOOR] Opened — reason: %s\n", reason);
}

void closeDoor() {
    if (doorState == DOOR_CLOSED || doorState == DOOR_CLOSING) return;
    doorState = DOOR_CLOSING;
    showLCD(" Closing...   ", "");

    for (int angle = DOOR_OPEN_ANGLE; angle >= DOOR_CLOSE_ANGLE; angle--) {
        long obstacle = readUltrasonic();
        if (obstacle > 0 && obstacle < ULTRASONIC_OBSTACLE_CM) {
            Serial.println(F("[SAFETY] Obstacle during close — reversing"));
            doorState = DOOR_OPEN;
            doorOpenedAt = millis();
            return;
        }
        doorServo.write(angle);
        delay(SERVO_MOVE_DELAY_MS);
    }

    digitalWrite(PIN_RELAY, LOW);
    doorState = DOOR_CLOSED;
    showLCD("  Door Locked ", " Scan card...  ");
    setLED(false, true);
    publishEvent("DOOR_CLOSED", "SYSTEM", "auto_close");
    Serial.println(F("[DOOR] Closed and locked"));
}

// ─── Ultrasonic ───────────────────────────────────────────────────────────────
long readUltrasonic() {
    digitalWrite(PIN_TRIG, LOW);
    delayMicroseconds(2);
    digitalWrite(PIN_TRIG, HIGH);
    delayMicroseconds(10);
    digitalWrite(PIN_TRIG, LOW);
    long duration = pulseIn(PIN_ECHO, HIGH, ULTRASONIC_TIMEOUT_US);
    if (duration == 0) return -1;
    return duration / 58L;   // convert to cm
}

// ─── RFID ─────────────────────────────────────────────────────────────────────
bool checkRFID(String& uid) {
    if (!rfid.PICC_IsNewCardPresent() || !rfid.PICC_ReadCardSerial()) return false;
    uid = "";
    for (byte i = 0; i < rfid.uid.size; i++) {
        if (rfid.uid.uidByte[i] < 0x10) uid += "0";
        uid += String(rfid.uid.uidByte[i], HEX);
    }
    uid.toUpperCase();
    rfid.PICC_HaltA();
    rfid.PCD_StopCrypto1();
    return true;
}

bool isAuthorized(const String& uid) {
    for (int i = 0; i < AUTHORIZED_COUNT; i++) {
        if (uid == String(AUTHORIZED_UIDS[i])) return true;
    }
    return false;
}

// ─── MQTT ─────────────────────────────────────────────────────────────────────
void mqttCallback(char* topic, byte* payload, unsigned int length) {
    String msg;
    for (unsigned int i = 0; i < length; i++) msg += (char)payload[i];
    msg.trim();
    Serial.printf("[MQTT] Received on %s: %s\n", topic, msg.c_str());

    if (msg == "OPEN")   openDoor("remote");
    else if (msg == "CLOSE") closeDoor();
    else if (msg == "STATUS") publishStatus();
}

void connectMQTT() {
    Serial.print(F("[MQTT] Connecting..."));
    if (mqtt.connect(MQTT_CLIENT_ID, MQTT_USER, MQTT_PASS)) {
        Serial.println(F(" connected"));
        mqtt.subscribe(TOPIC_COMMAND);
        publishStatus();
    } else {
        Serial.printf(" failed rc=%d\n", mqtt.state());
    }
}

void publishEvent(const char* event, const char* uid, const char* reason) {
    StaticJsonDocument<256> doc;
    doc["event"]     = event;
    doc["uid"]       = uid;
    doc["reason"]    = reason;
    doc["uptime_ms"] = millis();
    char buf[256];
    serializeJson(doc, buf);
    mqtt.publish(TOPIC_EVENT, buf, true);
}

void publishStatus() {
    StaticJsonDocument<128> doc;
    doc["state"]   = (doorState == DOOR_OPEN) ? "OPEN" : "CLOSED";
    doc["uptime"]  = millis() / 1000;
    doc["pir"]     = digitalRead(PIN_PIR);
    doc["dist_cm"] = readUltrasonic();
    char buf[128];
    serializeJson(doc, buf);
    mqtt.publish(TOPIC_STATUS, buf, true);
}

// ─── WiFi ─────────────────────────────────────────────────────────────────────
void connectWiFi() {
    Serial.printf("[WiFi] Connecting to %s", WIFI_SSID);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    unsigned long start = millis();
    while (WiFi.status() != WL_CONNECTED && millis() - start < WIFI_TIMEOUT_MS) {
        delay(500);
        Serial.print('.');
    }
    if (WiFi.status() == WL_CONNECTED) {
        Serial.printf("\n[WiFi] Connected — IP: %s\n", WiFi.localIP().toString().c_str());
    } else {
        Serial.println(F("\n[WiFi] Failed — running in offline mode"));
    }
}

// ─── UI Helpers ───────────────────────────────────────────────────────────────
void showLCD(const char* line1, const char* line2) {
    lcd.clear();
    lcd.setCursor(0, 0); lcd.print(line1);
    lcd.setCursor(0, 1); lcd.print(line2);
}

void buzzerAlert(int times, int durationMs) {
    for (int i = 0; i < times; i++) {
        digitalWrite(PIN_BUZZER, HIGH);
        delay(durationMs);
        digitalWrite(PIN_BUZZER, LOW);
        if (i < times - 1) delay(durationMs / 2);
    }
}

void setLED(bool red, bool green) {
    digitalWrite(PIN_LED_RED,   red   ? HIGH : LOW);
    digitalWrite(PIN_LED_GREEN, green ? HIGH : LOW);
}
