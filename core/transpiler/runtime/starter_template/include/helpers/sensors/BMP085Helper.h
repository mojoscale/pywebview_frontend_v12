#include <Adafruit_BMP085_U.h>
#include "PyDict.h"



bool custom_bmp085_helper_begin(Adafruit_BMP085_Unified* sensor, int mode) {
    // Cast the integer to bmp085_mode_t safely
    return sensor->begin(static_cast<bmp085_mode_t>(mode));
}



float custom_bmp085_helper_get_temperature(Adafruit_BMP085_Unified* sensor) {
    float temp = 0.0f;
    sensor->getTemperature(&temp);
    return temp;
}



float custom_bmp085_helper_get_pressure(Adafruit_BMP085_Unified* sensor) {
    float pressure = 0.0f;
    sensor->getPressure(&pressure);
    return pressure;
}



PyDict<float> custom_bmp085_helper_get_event(Adafruit_BMP085_Unified* sensor) {
    sensors_event_t event;
    PyDict<float> result;

    if (sensor->getEvent(&event)) {
        result.set("pressure", event.pressure);
        result.set("temperature", event.temperature);
    } else {
        result.set("pressure", 0.0f);
        result.set("temperature", 0.0f);
    }

    return result;
}


PyDict<String> custom_bmp085_helper_get_sensor_info(Adafruit_BMP085_Unified* sensor) {
    sensor_t details;
    PyDict<String> result;

    sensor->getSensor(&details);

    result.set("name", String(details.name));
    result.set("type", String(details.type));
    result.set("version", String(details.version));
    result.set("sensor_id", String(details.sensor_id));
    result.set("min_delay", String(details.min_delay));
    result.set("max_value", String(details.max_value));
    result.set("min_value", String(details.min_value));
    result.set("resolution", String(details.resolution));

    return result;
}

