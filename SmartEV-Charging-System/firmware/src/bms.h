#ifndef BMS_H
#define BMS_H

#include <Arduino.h>

// Battery state returned on every sensor poll
struct BatteryData {
    float voltage;        // Pack voltage (V)
    float current;        // Charge current (A), positive = charging
    float temperature;    // Cell temperature (°C)
    float ambientTemp;    // Ambient temperature (°C)
    float soc;            // State of Charge (0.0 – 100.0 %)
    float powerW;         // Instantaneous power (W)
    float energyWh;       // Cumulative energy this session (Wh)
    bool  isFault;        // True if any protection tripped
    char  faultReason[32];
};

class BMS {
public:
    BMS();
    void begin();
    BatteryData read();
    void resetSession();
    float getSessionEnergy() const;    // Wh accumulated this session
    bool  isFaultActive() const;
    void  clearFault();

private:
    float   _sessionEnergyWh;
    bool    _faultActive;
    char    _faultReason[32];
    unsigned long _lastPollMs;

    float estimateSOC(float voltage);
    bool  checkFaults(const BatteryData& data);
};

#endif // BMS_H
