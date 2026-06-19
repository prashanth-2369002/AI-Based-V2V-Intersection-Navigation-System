#include "auth.h"
#include "config.h"
#include <EEPROM.h>

Auth::Auth(MFRC522& rfid) : _rfid(rfid) {
    _lastUID[0] = '\0';
}

void Auth::begin() {
    EEPROM.begin(EEPROM_SIZE);
}

bool Auth::poll() {
    if (!_rfid.PICC_IsNewCardPresent() || !_rfid.PICC_ReadCardSerial()) {
        return false;
    }

    const byte* uid = _rfid.uid.uidByte;
    snprintf(_lastUID, sizeof(_lastUID), "%02X%02X%02X%02X",
             uid[0], uid[1], uid[2], uid[3]);

    byte stored[MAX_STORED_UIDS][UID_BYTES];
    loadUIDs(stored);

    _rfid.PICC_HaltA();
    _rfid.PCD_StopCrypto1();

    return matchUID(uid, stored);
}

const char* Auth::getLastUID() const {
    return _lastUID;
}

bool Auth::loadUIDs(byte stored[MAX_STORED_UIDS][UID_BYTES]) {
    for (int i = 0; i < MAX_STORED_UIDS; i++) {
        for (int b = 0; b < UID_BYTES; b++) {
            stored[i][b] = EEPROM.read(EEPROM_ADDR_UID_BASE + i * UID_BYTES + b);
        }
    }
    return true;
}

bool Auth::matchUID(const byte candidate[UID_BYTES],
                    const byte stored[MAX_STORED_UIDS][UID_BYTES]) {
    for (int i = 0; i < MAX_STORED_UIDS; i++) {
        bool match = true;
        for (int b = 0; b < UID_BYTES; b++) {
            if (candidate[b] != stored[i][b]) {
                match = false;
                break;
            }
        }
        if (match) return true;
    }
    return false;
}

bool Auth::registerUID(const byte uid[UID_BYTES]) {
    // Find first empty slot (all 0xFF = empty)
    for (int i = 0; i < MAX_STORED_UIDS; i++) {
        int addr  = EEPROM_ADDR_UID_BASE + i * UID_BYTES;
        bool empty = true;
        for (int b = 0; b < UID_BYTES; b++) {
            if (EEPROM.read(addr + b) != 0xFF) { empty = false; break; }
        }
        if (empty) {
            for (int b = 0; b < UID_BYTES; b++) {
                EEPROM.write(addr + b, uid[b]);
            }
            EEPROM.commit();
            return true;
        }
    }
    return false;  // No empty slot
}
