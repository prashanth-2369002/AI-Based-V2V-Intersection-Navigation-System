/*
 * RFID Module — MFRC522 (SPI interface)
 * Reads Mifare Classic / NTAG cards and returns UID as uppercase hex string.
 *
 * SPI pins (ESP32): SCK=18, MOSI=23, MISO=19, CS=5, RST=22
 */

#ifndef RFID_READER_INO
#define RFID_READER_INO

#include <MFRC522.h>
#include <SPI.h>
#include "config.h"

MFRC522 rfidModule(PIN_RFID_CS, PIN_RFID_RST);

void rfidInit() {
    SPI.begin();
    rfidModule.PCD_Init();
    delay(4);
    rfidModule.PCD_DumpVersionToSerial();
    Serial.println(F("[RFID] Module ready"));
}

// Returns true and fills uid string if a card is scanned
bool rfidReadUID(String& uid) {
    if (!rfidModule.PICC_IsNewCardPresent()) return false;
    if (!rfidModule.PICC_ReadCardSerial())   return false;

    uid = "";
    for (byte i = 0; i < rfidModule.uid.size; i++) {
        if (rfidModule.uid.uidByte[i] < 0x10) uid += "0";
        uid += String(rfidModule.uid.uidByte[i], HEX);
    }
    uid.toUpperCase();

    rfidModule.PICC_HaltA();
    rfidModule.PCD_StopCrypto1();
    Serial.printf("[RFID] Card UID: %s\n", uid.c_str());
    return true;
}

bool rfidIsAuthorized(const String& uid) {
    for (int i = 0; i < AUTHORIZED_COUNT; i++) {
        if (uid.equals(AUTHORIZED_UIDS[i])) return true;
    }
    return false;
}

// Utility: print all authorized UIDs to serial (for debugging)
void rfidPrintAuthorizedList() {
    Serial.println(F("[RFID] Authorized UIDs:"));
    for (int i = 0; i < AUTHORIZED_COUNT; i++) {
        Serial.printf("  [%d] %s\n", i, AUTHORIZED_UIDS[i]);
    }
}

#endif
