#ifndef BLESIMPLEHELPER_H
#define BLESIMPLEHELPER_H

#include <Arduino.h>
#include <BLEDevice.h>
#include "PyList.h"
#include "PyDict.h"
#include "BLESimple.h"

/**
 * Attempt to list all available BLE services.
 * This helper relies on BLEDevice APIs available in Arduino.
 * If full introspection isn't supported, it returns an empty list.
 */
PyList<String> get_all_ble_services(BLESimple &ble) {
    PyList<String> services;

    // Try to access BLE server (if available)
    BLEServer *server = BLEDevice::createServer();
    if (!server) {
        Serial.println("[BLEHelper] Warning: No BLEServer instance found.");
        return services;
    }

    // Arduino BLE doesn't expose service iteration, so we add a dummy placeholder.
    // In most cases, this must be manually populated elsewhere.
    Serial.println("[BLEHelper] Note: Arduino BLE API does not expose service introspection.");
    Serial.println("[BLEHelper] Returning an empty PyList<String> for compatibility.");

    // If you have at least one known service (like in your sketch),
    // you could append it manually here:
    // services.append("1234"); // Example: static fallback
    return services;
}

/**
 * Returns all characteristic UUIDs (with their last known values if possible)
 * for a given service UUID, using the Arduino BLE API.
 * 
 * Since Arduino BLE does not expose runtime introspection for characteristics,
 * this function safely returns an empty PyDict or placeholder entries.
 */
PyDict<String> get_characteristics_for_service(BLESimple &ble, const String &service_uuid) {
    PyDict<String> result;

    // In Arduino BLE, we cannot query the service list dynamically.
    // So this function will safely return an empty dict.
    // This ensures your transpiler never crashes, even when BLE internals are not introspectable.
    Serial.println("[BLEHelper] Warning: Arduino BLE API does not provide getCharacteristics().");
    Serial.println("[BLEHelper] Returning empty PyDict<String>.");

    // You can optionally add static test entries for debugging:
    // result.set("A001", "Hello");
    // result.set("A002", "World");
    return result;
}

/**
 * Checks if the current BLE peripheral (from BLESimple) is connected to any central device.
 *
 * @param ble  Reference to your BLESimple instance
 * @return true if at least one central is connected, false otherwise
 */
bool ble_is_connected(BLESimple &ble) {
    // Try to obtain the BLEServer instance.
    // Most Arduino BLE stacks keep a global server object after BLEDevice::createServer() is called.
    BLEServer *server = BLEDevice::createServer();
    if (!server) {
        Serial.println("[BLEHelper] ⚠️ No BLEServer instance found.");
        return false;
    }

    // Check the number of connected centrals (available in Arduino BLE core)
    uint8_t connectedCount = server->getConnectedCount();

    if (connectedCount > 0) {
        // Optional: debug output
        // Serial.printf("[BLEHelper] ✅ %d central(s) connected.\n", connectedCount);
        return true;
    } else {
        // Serial.println("[BLEHelper] 🔄 No active BLE connection.");
        return false;
    }
}


#endif
