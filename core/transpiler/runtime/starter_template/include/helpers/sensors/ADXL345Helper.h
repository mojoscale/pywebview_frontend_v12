#include <Adafruit_ADXL345_U.h>
#include "PyList.h"

PyList<float> custom_adxl345_helper_read_acceleration(Adafruit_ADXL345_Unified* sensor) {
    sensors_event_t event;
    float x = 0.0, y = 0.0, z = 0.0;

    if (sensor->getEvent(&event)) {
        x = event.acceleration.x;
        y = event.acceleration.y;
        z = event.acceleration.z;
    }

    return PyList<float>::from({x, y, z});
}
