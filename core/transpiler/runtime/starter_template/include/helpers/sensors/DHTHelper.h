
#include <DHT.h>
#include "../../PyDict.h"
#include <cstring>  // for strcmp


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

// Helper factory function
DHT createDHTSensor(uint8_t pin, String typeStr) {
    uint8_t sensorType;

    if (!typeStr.length()) {
        sensorType = DHT11;
    } else if (typeStr == "DHT22") {
        sensorType = DHT22;
    } else if (typeStr == "DHT21") {
        sensorType = DHT21;
    } else if (typeStr == "DHT11") {
        sensorType = DHT11;
    } else {
        // fallback for unrecognized string
        sensorType = DHT11;
    }

    // Construct a DHT instance using the resolved sensor type
    DHT dht(pin, sensorType);

    return dht;
}