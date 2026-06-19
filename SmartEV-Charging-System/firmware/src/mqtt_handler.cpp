#include "mqtt_handler.h"
#include "config.h"
#include <ArduinoJson.h>

MQTTHandler::MQTTHandler() : _client(_wifiClient), _clientId(nullptr) {}

void MQTTHandler::begin(const char* broker, uint16_t port, const char* clientId) {
    _clientId = clientId;
    _client.setServer(broker, port);
    _client.setKeepAlive(60);
}

void MQTTHandler::loop() {
    if (!_client.connected()) reconnect();
    _client.loop();
}

bool MQTTHandler::isConnected() const {
    return _client.connected();
}

void MQTTHandler::publishTelemetry(const char* uid,
                                    float voltage, float current,
                                    float powerW,  float energyWh,
                                    float soc,     float tempC,
                                    unsigned long elapsedS) {
    StaticJsonDocument<256> doc;
    doc["uid"]       = uid;
    doc["voltage"]   = serialized(String(voltage,   2));
    doc["current"]   = serialized(String(current,   3));
    doc["power_w"]   = serialized(String(powerW,    2));
    doc["energy_wh"] = serialized(String(energyWh,  3));
    doc["soc"]       = serialized(String(soc,        1));
    doc["temp_c"]    = serialized(String(tempC,      1));
    doc["elapsed_s"] = elapsedS;

    char buf[256];
    serializeJson(doc, buf, sizeof(buf));
    publish(TOPIC_TELEMETRY, buf);
}

void MQTTHandler::publishSessionStart(const char* uid) {
    StaticJsonDocument<128> doc;
    doc["event"] = "session_start";
    doc["uid"]   = uid;

    char buf[128];
    serializeJson(doc, buf, sizeof(buf));
    publish(TOPIC_SESSION, buf);
}

void MQTTHandler::publishSessionEnd(const char* uid,
                                     float energyWh, float costRs,
                                     unsigned long durationS) {
    StaticJsonDocument<192> doc;
    doc["event"]      = "session_end";
    doc["uid"]        = uid;
    doc["energy_wh"]  = serialized(String(energyWh, 2));
    doc["cost_rs"]    = serialized(String(costRs,    2));
    doc["duration_s"] = durationS;

    char buf[192];
    serializeJson(doc, buf, sizeof(buf));
    publish(TOPIC_SESSION, buf);
}

void MQTTHandler::publishFault(const char* uid, const char* reason) {
    StaticJsonDocument<128> doc;
    doc["event"]  = "fault";
    doc["uid"]    = uid;
    doc["reason"] = reason;

    char buf[128];
    serializeJson(doc, buf, sizeof(buf));
    publish(TOPIC_FAULT, buf);
}

void MQTTHandler::reconnect() {
    // Non-blocking: attempt once per call; main loop will retry next iteration
    if (WiFi.status() != WL_CONNECTED) return;
    _client.connect(_clientId);
}

void MQTTHandler::publish(const char* topic, const char* payload) {
    if (_client.connected()) {
        _client.publish(topic, payload);
    }
    // If not connected, drop the message — EEPROM log is the persistent backup
}
