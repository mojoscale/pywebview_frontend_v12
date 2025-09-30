
#include <DHT.h>
#include "../../PyDict.h"


PyDict<float> custom_dht_helper_read(DHT& dht) {
    PyDict<float> result;

    float temperature = dht.readTemperature();  // Celsius
    float humidity = dht.readHumidity();        // %

    if (isnan(temperature) || isnan(humidity)) {
        Serial.println("Failed to read from DHT sensor!");
        return result;  // returns empty PyDict
    }

    result.set("temperature", temperature);
    result.set("humidity", humidity);

    return result;
}


