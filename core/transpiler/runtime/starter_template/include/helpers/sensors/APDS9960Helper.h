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
