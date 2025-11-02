#ifndef DALLASSENSORHELPER_H
#define DALLASSENSORHELPER_H

#include <Arduino.h>
#include <OneWire.h>
#include <DallasTemperature.h>

/**
 * @brief Create and initialize a DallasTemperature instance
 *        for a DS18B20 sensor on a given OneWire pin.
 *
 * This helper abstracts away the creation of the OneWire object
 * and initialization sequence, making it easier for high-level
 * frameworks (like your transpiler) to automatically instantiate
 * temperature sensors without user boilerplate.
 *
 * @param onewire_pin GPIO pin connected to the DS18B20 data line.
 * @return DallasTemperature* Pointer to a ready-to-use DallasTemperature instance.
 */
inline DallasTemperature* create_dallas_sensor(int onewire_pin) {
    // Allocate OneWire on heap
    OneWire* oneWire = new OneWire(onewire_pin);

    // Allocate DallasTemperature using that OneWire bus
    DallasTemperature* sensors = new DallasTemperature(oneWire);

    // Initialize communication
    sensors->begin();

    Serial.printf("✅ DallasTemperature initialized on OneWire pin %d\n", onewire_pin);
    return sensors;
}

#endif // DALLASSENSORHELPER_H
