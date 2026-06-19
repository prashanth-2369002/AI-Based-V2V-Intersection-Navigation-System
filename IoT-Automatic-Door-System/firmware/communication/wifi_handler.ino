/*
 * WiFi Handler — ESP32
 * Manages connection, reconnection, and status reporting.
 */

#ifndef WIFI_HANDLER_INO
#define WIFI_HANDLER_INO

#include <WiFi.h>
#include "config.h"

static bool wifiConnected = false;

void wifiConnect() {
    Serial.printf("[WiFi] Connecting to SSID: %s\n", WIFI_SSID);
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

    unsigned long start = millis();
    while (WiFi.status() != WL_CONNECTED) {
        if (millis() - start > WIFI_TIMEOUT_MS) {
            Serial.println(F("[WiFi] Timeout — offline mode"));
            wifiConnected = false;
            return;
        }
        delay(500);
        Serial.print('.');
    }

    wifiConnected = true;
    Serial.printf("\n[WiFi] Connected — IP: %s  RSSI: %d dBm\n",
                  WiFi.localIP().toString().c_str(), WiFi.RSSI());
}

void wifiMaintain() {
    if (WiFi.status() != WL_CONNECTED) {
        wifiConnected = false;
        Serial.println(F("[WiFi] Dropped — reconnecting..."));
        wifiConnect();
    }
}

bool wifiIsConnected() { return wifiConnected && WiFi.status() == WL_CONNECTED; }

String wifiGetIP()   { return WiFi.localIP().toString(); }
int    wifiGetRSSI() { return WiFi.RSSI(); }

#endif
