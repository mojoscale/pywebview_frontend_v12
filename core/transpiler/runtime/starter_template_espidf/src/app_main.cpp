#include <Arduino.h>

// Forward declarations from main.cpp
extern void setup();
extern void loop();

extern "C" void app_main() {
    // ESP-IDF specific initialization
    initArduino();
    
    // Optional: ESP-IDF specific configuration
    // Serial.setDebugOutput(true);
    
    printf("ESP-IDF bridge started - running Arduino code...\n");
    
    // That's it! Arduino setup() and loop() will be called automatically
    // by initArduino() in the background
}