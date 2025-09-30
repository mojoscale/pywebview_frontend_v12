
#include <MHZ19.h>


MHZ19 custom_mhz19_helper_create_mhz19(Stream &stream) {
    MHZ19 sensor;
    sensor.begin(stream);
    return sensor;
}
