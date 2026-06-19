/*
 * Ultrasonic Sensor Module — HC-SR04
 * Range: 2 cm – 400 cm | Resolution: ~0.3 cm
 *
 * Used for two distinct purposes:
 *   1. Proximity trigger: person within ULTRASONIC_TRIGGER_CM
 *   2. Obstacle safety: object within ULTRASONIC_OBSTACLE_CM during door swing
 */

#ifndef ULTRASONIC_SENSOR_INO
#define ULTRASONIC_SENSOR_INO

#include "config.h"

void ultrasonicInit() {
    pinMode(PIN_TRIG, OUTPUT);
    pinMode(PIN_ECHO, INPUT);
    digitalWrite(PIN_TRIG, LOW);
    Serial.println(F("[ULTRASONIC] Initialized"));
}

// Returns distance in cm, or -1 on timeout
long ultrasonicRead() {
    digitalWrite(PIN_TRIG, LOW);
    delayMicroseconds(2);
    digitalWrite(PIN_TRIG, HIGH);
    delayMicroseconds(10);
    digitalWrite(PIN_TRIG, LOW);

    long duration = pulseIn(PIN_ECHO, HIGH, ULTRASONIC_TIMEOUT_US);
    if (duration == 0) return -1;
    return duration / 58L;
}

// Returns average of N readings (filters noise)
long ultrasonicReadAvg(int samples) {
    long sum = 0;
    int valid = 0;
    for (int i = 0; i < samples; i++) {
        long d = ultrasonicRead();
        if (d > 0) { sum += d; valid++; }
        delay(10);
    }
    return (valid > 0) ? (sum / valid) : -1;
}

bool isPersonInRange() {
    long d = ultrasonicReadAvg(3);
    if (d < 0) return false;
    Serial.printf("[ULTRASONIC] Distance: %ld cm\n", d);
    return d <= ULTRASONIC_TRIGGER_CM;
}

bool isObstaclePresent() {
    long d = ultrasonicRead();
    return (d > 0 && d < ULTRASONIC_OBSTACLE_CM);
}

#endif
