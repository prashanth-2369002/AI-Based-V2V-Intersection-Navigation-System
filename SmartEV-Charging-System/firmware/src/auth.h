#ifndef AUTH_H
#define AUTH_H

#include <Arduino.h>
#include <MFRC522.h>

#define MAX_STORED_UIDS   4
#define UID_BYTES         4

class Auth {
public:
    Auth(MFRC522& rfid);
    void begin();

    // Returns true if a card was presented and UID matched
    bool poll();

    // Returns UID of the last scanned card as hex string
    const char* getLastUID() const;

    // Register a new UID into EEPROM (called during provisioning)
    bool registerUID(const byte uid[UID_BYTES]);

private:
    MFRC522& _rfid;
    char     _lastUID[12];   // 4 bytes → 8 hex chars + null

    bool loadUIDs(byte stored[MAX_STORED_UIDS][UID_BYTES]);
    bool matchUID(const byte candidate[UID_BYTES],
                  const byte stored[MAX_STORED_UIDS][UID_BYTES]);
};

#endif // AUTH_H
