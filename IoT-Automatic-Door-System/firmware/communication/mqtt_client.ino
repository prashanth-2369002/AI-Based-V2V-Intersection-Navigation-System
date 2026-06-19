/*
 * MQTT Client — PubSubClient wrapper
 * Handles connect, reconnect, publish, subscribe, and offline queue.
 */

#ifndef MQTT_CLIENT_INO
#define MQTT_CLIENT_INO

#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include "config.h"

extern WiFiClient  wifiClient;
extern PubSubClient mqtt;

// Simple offline queue (holds up to 10 messages when broker is unreachable)
struct QueuedMsg { char topic[64]; char payload[256]; };
static QueuedMsg  msgQueue[10];
static int        queueHead = 0, queueTail = 0;

static void enqueue(const char* topic, const char* payload) {
    int next = (queueTail + 1) % 10;
    if (next == queueHead) return;  // queue full — drop oldest
    strncpy(msgQueue[queueTail].topic,   topic,   63);
    strncpy(msgQueue[queueTail].payload, payload, 255);
    queueTail = next;
}

static void drainQueue() {
    while (queueHead != queueTail && mqtt.connected()) {
        mqtt.publish(msgQueue[queueHead].topic,
                     msgQueue[queueHead].payload, true);
        queueHead = (queueHead + 1) % 10;
    }
}

void mqttPublish(const char* topic, const char* payload) {
    if (mqtt.connected()) {
        mqtt.publish(topic, payload, true);
        drainQueue();
    } else {
        enqueue(topic, payload);
    }
}

void mqttPublishJson(const char* topic, const JsonDocument& doc) {
    char buf[256];
    serializeJson(doc, buf, sizeof(buf));
    mqttPublish(topic, buf);
}

void mqttConnect() {
    if (mqtt.connected()) return;
    Serial.print(F("[MQTT] Connecting..."));
    bool ok = (strlen(MQTT_USER) > 0)
        ? mqtt.connect(MQTT_CLIENT_ID, MQTT_USER, MQTT_PASS)
        : mqtt.connect(MQTT_CLIENT_ID);

    if (ok) {
        Serial.println(F(" OK"));
        mqtt.subscribe(TOPIC_COMMAND);
        drainQueue();
    } else {
        Serial.printf(" FAIL rc=%d\n", mqtt.state());
    }
}

void mqttMaintain() {
    if (!mqtt.connected()) mqttConnect();
    mqtt.loop();
}

#endif
