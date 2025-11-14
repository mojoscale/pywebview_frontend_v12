#include "SafeSerial.h"

bool SafeSerial::_serial_ready = false;

void SafeSerial::begin(unsigned long baudrate, SerialMode mode, unsigned long timeout_ms) {
    Serial.begin(baudrate);
    
    switch(mode) {
        case BLOCKING:
            // Wait indefinitely for serial connection (for debugging)
            while (!Serial) {
                ; // Wait for serial port to connect
            }
            _serial_ready = true;
            break;
            
        case NON_BLOCKING:
            // Don't wait at all (for production)
            _serial_ready = true;
            break;
            
        case TIMEOUT:
        default:
            // Wait with timeout (balanced approach)
            unsigned long start_time = millis();
            while (!Serial && (millis() - start_time < timeout_ms)) {
                ; // Wait for serial port with timeout
            }
            _serial_ready = true;
            break;
    }
    
    // Small delay to ensure serial stabilizes
    delay(100);
}

bool SafeSerial::isConnected() {
    return Serial && _serial_ready;
}

void SafeSerial::print(const String& message) {
    if (isConnected()) {
        Serial.print(message);
    }
    // Optional: Add other output methods here (LCD, LED, etc.)
}

void SafeSerial::println(const String& message) {
    if (isConnected()) {
        Serial.println(message);
    }
    // Optional: Add other output methods here
}