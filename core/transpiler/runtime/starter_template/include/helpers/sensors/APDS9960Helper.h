#include "Adafruit_APDS9960.h"
#include "PyList.h"

PyList<int> custom_apds9960_helper_get_color_data(Adafruit_APDS9960& sensor) {
    uint16_t r, g, b, c;
    sensor.getColorData(&r, &g, &b, &c);  // Corrected from sensor-> to sensor.

    PyList<int> result;
    result.append((int)r);
    result.append((int)g);
    result.append((int)b);
    result.append((int)c);

    return result;
}


// Custom helper for sensor begin with gain as int
bool custom_apds9960_helper_begin(Adafruit_APDS9960& sensor, int iTimeMS, int gain, int address) {
    apds9960AGain_t gain_enum;

    switch (gain) {
        case 0:
            gain_enum = APDS9960_AGAIN_1X;
            break;
        case 1:
            gain_enum = APDS9960_AGAIN_4X;
            break;
        case 2:
            gain_enum = APDS9960_AGAIN_16X;
            break;
        case 3:
            gain_enum = APDS9960_AGAIN_64X;
            break;
        default:
            // fallback or invalid gain value
            gain_enum = APDS9960_AGAIN_4X;  // reasonable default
            break;
    }

    return sensor.begin(iTimeMS, gain_enum, address);
}



void setAPDS9960ADCGain(Adafruit_APDS9960& sensor, int gain_val) {
    apds9960AGain_t gain_enum;

    switch (gain_val) {
        case 0:
            gain_enum = APDS9960_AGAIN_1X;
            break;
        case 1:
            gain_enum = APDS9960_AGAIN_4X;
            break;
        case 2:
            gain_enum = APDS9960_AGAIN_16X;
            break;
        case 3:
            gain_enum = APDS9960_AGAIN_64X;
            break;
        default:
            gain_enum = APDS9960_AGAIN_1X;  // fallback for invalid input
            break;
    }

    sensor.setADCIntegrationTime(10); // optional: adjust integration time if needed
    sensor.setADCGain(gain_enum);
}


inline void configureAPDS9960LED(Adafruit_APDS9960 &sensor, int drive_mA, int boost_percent) {
    apds9960LedDrive_t driveEnum;
    if (drive_mA >= 100) driveEnum = APDS9960_LEDDRIVE_100MA;
    else if (drive_mA >= 50) driveEnum = APDS9960_LEDDRIVE_50MA;
    else if (drive_mA >= 25) driveEnum = APDS9960_LEDDRIVE_25MA;
    else driveEnum = APDS9960_LEDDRIVE_12MA;

    apds9960LedBoost_t boostEnum;
    if (boost_percent >= 300) boostEnum = APDS9960_LEDBOOST_300PCNT;
    else if (boost_percent >= 200) boostEnum = APDS9960_LEDBOOST_200PCNT;
    else if (boost_percent >= 150) boostEnum = APDS9960_LEDBOOST_150PCNT;
    else boostEnum = APDS9960_LEDBOOST_100PCNT;

    sensor.setLED(driveEnum, boostEnum);
}



inline void configureAPDS9960ProxGain(Adafruit_APDS9960 &sensor, int gainCode) {
    apds9960PGain_t gainEnum;
    if (gainCode == 3) gainEnum = APDS9960_PGAIN_8X;
    else if (gainCode == 2) gainEnum = APDS9960_PGAIN_4X;
    else if (gainCode == 1) gainEnum = APDS9960_PGAIN_2X;
    else gainEnum = APDS9960_PGAIN_1X;

    sensor.setProxGain(gainEnum);
}



inline void configureAPDS9960ProxPulse(Adafruit_APDS9960 &sensor, int pulse_len, int pulses) {
    apds9960PPulseLen_t lenEnum;
    if (pulse_len == 3) lenEnum = APDS9960_PPULSELEN_32US;
    else if (pulse_len == 2) lenEnum = APDS9960_PPULSELEN_16US;
    else if (pulse_len == 1) lenEnum = APDS9960_PPULSELEN_8US;
    else lenEnum = APDS9960_PPULSELEN_4US;

    sensor.setProxPulse(lenEnum, static_cast<uint8_t>(pulses));
}