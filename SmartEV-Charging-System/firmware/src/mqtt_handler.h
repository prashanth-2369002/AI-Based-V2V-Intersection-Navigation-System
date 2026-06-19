#ifndef MQTT_HANDLER_H
#define MQTT_HANDLER_H

#include <Arduino.h>
#include <PubSubClient.h>
#include <WiFi.h>

/*
 * Thin wrapper around PubSubClient.
 * Handles connection, reconnection, and JSON payload assembly
 * so main.ino stays focused on state machine logic.
 */
class MQTTHandler {
public:
    MQTTHandler();

    void begin(const char* broker, uint16_t port, const char* clientId);
    void loop();                    // Must be called every main loop iteration
    bool isConnected() const;

    // Structured publish helpers
    void publishTelemetry(const char* uid,
                          float voltage, float current,
                          float powerW,  float energyWh,
                          float soc,     float tempC,
                          unsigned long elapsedS);

    void publishSessionStart(const char* uid);

    void publishSessionEnd(const char* uid,
                           float energyWh, float costRs,
                           unsigned long durationS);

    void publishFault(const char* uid, const char* reason);

private:
    WiFiClient    _wifiClient;
    PubSubClient  _client;
    const char*   _clientId;

    void reconnect();
    void publish(const char* topic, const char* payload);
};

#endif // MQTT_HANDLER_H
