#include <Arduino.h>
#include <MQ2.h>
#include "PyDict.h"

/**
 * Reads LPG, CO, and SMOKE values from the MQ2 sensor
 * and returns them as a PyDict<float> object.
 *
 * @param sensor Reference to an MQ2 instance.
 * @param print  If true, enables Serial printing inside MQ2::read().
 * @return PyDict<float> Dictionary-style container with keys "LPG", "CO", "SMOKE".
 */
PyDict<float> custom_mq2_helper_read_dict(MQ2& sensor, bool print) {
    float* values = sensor.read(print);  // [LPG, CO, SMOKE]
    PyDict<float> result;
    result.set("LPG", values[0]);
    result.set("CO", values[1]);
    result.set("SMOKE", values[2]);
    return result;
}
