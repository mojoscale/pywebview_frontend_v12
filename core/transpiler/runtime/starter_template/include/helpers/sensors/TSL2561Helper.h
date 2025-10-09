#ifndef TSL2561_HELPER_H
#define TSL2561_HELPER_H

#include <Arduino.h>
#include <Adafruit_TSL2561_U.h>
#include "PyList.h"

/**
 * Custom helper functions for TSL2561 Unified sensor
 * (safe for transpiler integer arguments)
 */

inline void custom_tsl2561_helper_set_gain(Adafruit_TSL2561_Unified* sensor, int gain_mode) {
    if (!sensor) return;

    tsl2561Gain_t gain_enum;
    switch (gain_mode) {
        case 0:
            gain_enum = TSL2561_GAIN_1X;   // 1x gain (low)
            break;
        case 1:
        default:
            gain_enum = TSL2561_GAIN_16X;  // 16x gain (high)
            break;
    }
    sensor->setGain(gain_enum);
}

inline void custom_tsl2561_helper_set_integration_time(Adafruit_TSL2561_Unified* sensor, int integration_mode) {
    if (!sensor) return;

    tsl2561IntegrationTime_t time_enum;
    switch (integration_mode) {
        case 0:
            time_enum = TSL2561_INTEGRATIONTIME_13MS;
            break;
        case 1:
            time_enum = TSL2561_INTEGRATIONTIME_101MS;
            break;
        case 2:
        default:
            time_enum = TSL2561_INTEGRATIONTIME_402MS;
            break;
    }
    sensor->setIntegrationTime(time_enum);
}

/**
 * Reads broadband and IR values using getLuminosity()
 * Returns a PyList<int> [broadband, ir].
 */
inline PyList<int> custom_tsl2561_helper_get_luminosity(Adafruit_TSL2561_Unified* sensor) {
    PyList<int> result;
    if (!sensor) return result;

    uint16_t broadband = 0, ir = 0;
    sensor->getLuminosity(&broadband, &ir);
    result.append(static_cast<int>(broadband));
    result.append(static_cast<int>(ir));
    return result;
}

#endif  // TSL2561_HELPER_H
