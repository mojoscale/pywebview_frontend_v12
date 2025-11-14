#ifndef SAFE_SERIAL_H
#define SAFE_SERIAL_H

#include <Arduino.h>

class SafeSerial {
public:
    enum SerialMode {
        BLOCKING,      // Wait for serial (debug mode)
        NON_BLOCKING,  // Don't wait (production mode)
        TIMEOUT        // Wait with timeout
    };

    static void begin(unsigned long baudrate = 115200, 
                     SerialMode mode = TIMEOUT, 
                     unsigned long timeout_ms = 5000);
    
    static bool isConnected();
    static void print(const String& message);
    static void println(const String& message);
    
private:
    static bool _serial_ready;
};

#endif