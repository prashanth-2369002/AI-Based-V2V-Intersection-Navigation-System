/*
 * PIR Sensor Module — HC-SR501
 * Handles motion detection and debouncing.
 *
 * The HC-SR501 outputs HIGH for ~3 s after motion ends.
 * We gate its output with a cooldown to avoid repeated triggers.
 */

#ifndef PIR_SENSOR_INO
#define PIR_SENSOR_INO

#include "config.h"

static unsigned long pirLastTrigger = 0;
static const unsigned long PIR_COOLDOWN_MS = 2000;

bool pirMotionDetected() {
    if (digitalRead(PIN_PIR) == HIGH) {
        if (millis() - pirLastTrigger > PIR_COOLDOWN_MS) {
            pirLastTrigger = millis();
            Serial.println(F("[PIR] Motion detected"));
            return true;
        }
    }
    return false;
}

void pirInit() {
    pinMode(PIN_PIR, INPUT);
    Serial.printf("[PIR] Warming up for %d ms...\n", PIR_WARMUP_MS);
    delay(PIR_WARMUP_MS);
    Serial.println(F("[PIR] Ready"));
}

#endif
