#include "bms.h"
#include "config.h"
#include <Adafruit_INA219.h>
#include <OneWire.h>
#include <DallasTemperature.h>

static Adafruit_INA219 ina219(INA219_ADDR);
static OneWire          oneWire(PIN_DS18B20);
static DallasTemperature sensors(&oneWire);

// Voltage → SOC lookup table for Li-ion 3S (per-cell voltage)
// Source: typical 18650 discharge curve at 0.5C
static const float SOC_TABLE_VOLT[] = {3.00, 3.20, 3.40, 3.60, 3.70, 3.80, 3.90, 4.00, 4.10, 4.20};
static const float SOC_TABLE_PCT[]  = {0,    5,    10,   30,   50,   70,   85,   93,   98,   100};
static const int   SOC_TABLE_SIZE   = 10;

BMS::BMS()
    : _sessionEnergyWh(0.0f), _faultActive(false), _lastPollMs(0) {
    _faultReason[0] = '\0';
}

void BMS::begin() {
    ina219.begin();
    ina219.setCalibration_16V_400mA();  // Adjust for 5A ACS712 in parallel if needed
    sensors.begin();
}

void BMS::resetSession() {
    _sessionEnergyWh = 0.0f;
    _faultActive     = false;
    _faultReason[0]  = '\0';
    _lastPollMs      = millis();
}

BatteryData BMS::read() {
    BatteryData data = {};

    data.voltage     = ina219.getBusVoltage_V();
    data.current     = ina219.getCurrent_mA() / 1000.0f;  // Convert mA → A
    data.powerW      = data.voltage * data.current;

    // Integrate energy: P(W) × dt(h) = E(Wh)
    unsigned long now = millis();
    if (_lastPollMs > 0) {
        float dtHours         = (now - _lastPollMs) / 3600000.0f;
        _sessionEnergyWh     += data.powerW * dtHours;
    }
    _lastPollMs = now;

    data.energyWh = _sessionEnergyWh;

    // Temperature (sensor index 0 = cell, 1 = ambient)
    sensors.requestTemperatures();
    data.temperature  = sensors.getTempCByIndex(0);
    data.ambientTemp  = sensors.getTempCByIndex(1);

    // SOC from per-cell voltage
    float perCellVolt = data.voltage / (float)CELL_COUNT;
    data.soc          = estimateSOC(perCellVolt);

    // Safety checks
    data.isFault    = checkFaults(data);
    if (data.isFault) {
        strncpy(data.faultReason, _faultReason, sizeof(data.faultReason) - 1);
    }

    return data;
}

float BMS::estimateSOC(float cellVoltage) {
    if (cellVoltage <= SOC_TABLE_VOLT[0]) return SOC_TABLE_PCT[0];
    if (cellVoltage >= SOC_TABLE_VOLT[SOC_TABLE_SIZE - 1]) return SOC_TABLE_PCT[SOC_TABLE_SIZE - 1];

    for (int i = 1; i < SOC_TABLE_SIZE; i++) {
        if (cellVoltage <= SOC_TABLE_VOLT[i]) {
            float ratio = (cellVoltage - SOC_TABLE_VOLT[i - 1]) /
                          (SOC_TABLE_VOLT[i] - SOC_TABLE_VOLT[i - 1]);
            return SOC_TABLE_PCT[i - 1] + ratio * (SOC_TABLE_PCT[i] - SOC_TABLE_PCT[i - 1]);
        }
    }
    return 100.0f;
}

bool BMS::checkFaults(const BatteryData& data) {
    float perCell = data.voltage / (float)CELL_COUNT;

    if (perCell > VOLT_CUTOFF_PER_CELL) {
        snprintf(_faultReason, sizeof(_faultReason), "OVP: %.2fV/cell", perCell);
        _faultActive = true;
    } else if (data.temperature > TEMP_CUTOFF_C) {
        snprintf(_faultReason, sizeof(_faultReason), "OTP: %.1fC", data.temperature);
        _faultActive = true;
    } else if (data.current > CURRENT_MAX_A) {
        snprintf(_faultReason, sizeof(_faultReason), "OCP: %.2fA", data.current);
        _faultActive = true;
    }

    return _faultActive;
}

float BMS::getSessionEnergy() const { return _sessionEnergyWh; }
bool  BMS::isFaultActive()    const { return _faultActive; }
void  BMS::clearFault() {
    _faultActive    = false;
    _faultReason[0] = '\0';
}
