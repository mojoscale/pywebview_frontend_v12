#ifndef VL53L0X_HELPER_H
#define VL53L0X_HELPER_H

#include <Adafruit_VL53L0X.h>

// -----------------------------------------------------------------------------
// Convert integer mode → Adafruit_VL53L0X::VL53L0X_Sense_config_t
// -----------------------------------------------------------------------------
inline bool custom_vl53l0x_helper_config_sensor(Adafruit_VL53L0X& sensor, int mode) {
    Adafruit_VL53L0X::VL53L0X_Sense_config_t cfg;

    switch (mode) {
        case 0:
            cfg = Adafruit_VL53L0X::VL53L0X_SENSE_DEFAULT;
            break;
        case 1:
            cfg = Adafruit_VL53L0X::VL53L0X_SENSE_LONG_RANGE;
            break;
        case 2:
            cfg = Adafruit_VL53L0X::VL53L0X_SENSE_HIGH_SPEED;
            break;
        case 3:
            cfg = Adafruit_VL53L0X::VL53L0X_SENSE_HIGH_ACCURACY;
            break;
        default:
            return false;
    }

    return sensor.configSensor(cfg);
}

#endif  // VL53L0X_HELPER_H
