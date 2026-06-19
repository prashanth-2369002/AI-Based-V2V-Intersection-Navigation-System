#include "payment.h"
#include "config.h"
#include <EEPROM.h>

Payment::Payment() : _active(false), _startMs(0), _logSlot(0) {
    _uid[0] = '\0';
}

void Payment::startSession(const char* uid) {
    strncpy(_uid, uid, sizeof(_uid) - 1);
    _startMs = millis();
    _active  = true;
}

SessionRecord Payment::endSession(float energyWh) {
    SessionRecord rec = {};
    strncpy(rec.uid, _uid, sizeof(rec.uid) - 1);
    rec.startMs  = _startMs;
    rec.endMs    = millis();
    rec.energyWh = energyWh;
    rec.costRs   = calculateCost(energyWh);

    _active = false;
    return rec;
}

float Payment::calculateCost(float energyWh) const {
    float kWh = energyWh / 1000.0f;
    return kWh * UNIT_RATE_RS;
}

unsigned long Payment::getElapsedSeconds() const {
    if (!_active) return 0;
    return (millis() - _startMs) / 1000UL;
}

bool Payment::isSessionActive() const {
    return _active;
}

void Payment::logToEEPROM(const SessionRecord& record) {
    int addr = EEPROM_ADDR_LOG_BASE + (_logSlot % MAX_SESSION_LOGS) * SESSION_LOG_SIZE;

    // Write UID (4 bytes as packed hex is too complex for EEPROM — store first 4 chars)
    for (int i = 0; i < 4 && i < (int)sizeof(record.uid); i++) {
        EEPROM.write(addr + i, (byte)record.uid[i]);
    }
    // Write energyWh as uint16 (Wh, max 65535)
    uint16_t whInt = (uint16_t)record.energyWh;
    EEPROM.write(addr + 4, highByte(whInt));
    EEPROM.write(addr + 5, lowByte(whInt));
    // Write costRs as uint16 (paise, cost * 100)
    uint16_t paise = (uint16_t)(record.costRs * 100.0f);
    EEPROM.write(addr + 6, highByte(paise));
    EEPROM.write(addr + 7, lowByte(paise));
    // Write duration as uint32 (seconds)
    uint32_t dur = (record.endMs - record.startMs) / 1000UL;
    EEPROM.write(addr + 8,  (dur >> 24) & 0xFF);
    EEPROM.write(addr + 9,  (dur >> 16) & 0xFF);
    EEPROM.write(addr + 10, (dur >> 8)  & 0xFF);
    EEPROM.write(addr + 11,  dur        & 0xFF);

    EEPROM.commit();
    _logSlot++;
}
