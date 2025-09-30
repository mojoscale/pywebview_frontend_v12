#include <Adafruit_Sensor.h>
#include <Adafruit_TSL2561_U.h>
#include "PyList.h"

PyList<int> custom_tsl2561_helper_get_luminosity(Adafruit_TSL2561_Unified& sensor) {
    uint16_t broadband = 0;
    uint16_t ir = 0;

    sensor.getLuminosity(&broadband, &ir);

    return PyList<int>::from({ static_cast<int>(broadband), static_cast<int>(ir) });
}
