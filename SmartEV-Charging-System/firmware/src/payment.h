#ifndef PAYMENT_H
#define PAYMENT_H

#include <Arduino.h>

struct SessionRecord {
    char  uid[12];          // User card UID
    unsigned long startMs;  // Session start timestamp (millis)
    unsigned long endMs;    // Session end timestamp
    float energyWh;         // Energy consumed (Wh)
    float costRs;           // Amount billed (₹)
};

class Payment {
public:
    Payment();

    void startSession(const char* uid);
    SessionRecord endSession(float energyWh);

    float calculateCost(float energyWh) const;
    unsigned long getElapsedSeconds() const;
    bool isSessionActive() const;

    // Persists record to EEPROM circular log
    void logToEEPROM(const SessionRecord& record);

private:
    bool          _active;
    char          _uid[12];
    unsigned long _startMs;
    int           _logSlot;   // Circular log pointer (0 – MAX_SESSION_LOGS-1)
};

#endif // PAYMENT_H
